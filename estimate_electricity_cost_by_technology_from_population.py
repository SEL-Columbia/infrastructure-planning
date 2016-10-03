import geometryIO
import re
import shutil
import simplejson as json
from argparse import ArgumentParser
from collections import OrderedDict
from geopy import GoogleV3
from geopy.distance import vincenty as get_distance
from invisibleroads_macros.disk import make_enumerated_folder_for, make_folder
from invisibleroads_macros.iterable import (
    OrderedDefaultDict, merge_dictionaries)
from invisibleroads_macros.log import format_summary
from invisibleroads_macros.math import divide_safely
from networkx import write_gpickle
from os.path import isabs, basename, join, splitext
from pandas import DataFrame, Series, concat
from shapely import wkt
from shapely.geometry import GeometryCollection, LineString, Point

from infrastructure_planning import parsers
from infrastructure_planning.exceptions import (
    InfrastructurePlanningError, UnsupportedFormat)
from infrastructure_planning.macros import (
    compute, get_graph_from_table, get_table_from_graph,
    get_table_from_variables)

from infrastructure_planning.demography.exponential import estimate_population
from infrastructure_planning.electricity.consumption import (
    estimate_consumption_profile)
from infrastructure_planning.electricity.consumption.linear import (
    estimate_consumption_from_connection_type)
from infrastructure_planning.electricity.demand import estimate_peak_demand
from infrastructure_planning.electricity.cost import (
    estimate_internal_cost_by_technology, estimate_external_cost_by_technology)
from infrastructure_planning.electricity.cost.grid import (
    estimate_grid_mv_line_budget)

from networker.networker_runner import NetworkerRunner
from sequencer import NetworkPlan
from sequencer import Sequencer


def assemble_total_mv_line_network(
        target_folder, infrastructure_graph, grid_mv_line_geotable,
        grid_mv_network_minimum_point_count):
    geocode = GoogleV3().geocode
    for node_id, node_d in infrastructure_graph.nodes_iter(data=True):
        lon = node_d.get('longitude')
        lat = node_d.get('latitude')
        if lon is None or lat is None:
            location = geocode(node_d['name'])
            lon, lat = location.longitude, location.latitude
        node_d.update(longitude=lon, latitude=lat)
    node_table = get_table_from_graph(infrastructure_graph, [
        'longitude', 'latitude', 'grid_mv_line_adjusted_budget_in_meters'])
    node_table_path = join(target_folder, 'nodes-networker.csv')
    node_table.to_csv(node_table_path)
    nwk_settings = {
        'demand_nodes': {
            'filename': node_table_path,
            'x_column': 'longitude',
            'y_column': 'latitude',
            'budget_column': 'grid_mv_line_adjusted_budget_in_meters',
        },
        'network_algorithm': 'mod_boruvka',
        'network_parameters': {
            'minimum_node_count': grid_mv_network_minimum_point_count,
        },
    }
    if len(grid_mv_line_geotable):
        grid_mv_line_shapefile_path = join(
            target_folder, 'existing_grid_mv_line.shp')
        save_shapefile(grid_mv_line_shapefile_path, grid_mv_line_geotable)
        nwk_settings['existing_networks'] = {
            'filename': grid_mv_line_shapefile_path,
            'budget_value': 0,
        }
    nwk = NetworkerRunner(nwk_settings, target_folder)
    nwk.validate()
    msf = nwk.run()
    for node_id in msf.nodes_iter():
        if node_id in infrastructure_graph:
            continue
        # Add fake nodes (I think that is what these are)
        longitude, latitude = msf.coords[node_id]
        infrastructure_graph.add_node(node_id, {
            'longitude': longitude,
            'latitude': latitude,
            'population': 0,
            'peak_demand_in_kw': 0,
        })
    infrastructure_graph.add_edges_from(msf.edges_iter())
    return {
        'infrastructure_graph': infrastructure_graph,
    }


def sequence_total_mv_line_network(target_folder, infrastructure_graph):
    if not infrastructure_graph.edges():
        return {}  # The network is empty and there is nothing to sequence
    node_table = get_table_from_graph(infrastructure_graph, [
        'longitude', 'latitude', 'population', 'peak_demand_in_kw'])
    node_table = node_table.rename(columns={'longitude': 'X', 'latitude': 'Y'})
    node_table = node_table[node_table.population > 0]  # Ignore fake nodes
    node_table_path = join(target_folder, 'nodes-sequencer.csv')
    node_table.to_csv(node_table_path)
    edge_shapefile_path = join(target_folder, 'edges.shp')
    nwp = NetworkPlan.from_files(
        edge_shapefile_path, node_table_path, prioritize='population',
        proj='+proj=longlat +datum=WGS84 +no_defs')
    model = Sequencer(nwp, 'peak.demand.in.kw')
    model.sequence()
    order_series = model.output_frame['Sequence..Far.sighted.sequence']
    for index, order in order_series.iteritems():
        node_id = model.output_frame['Unnamed..0'][index]
        infrastructure_graph.node[node_id]['order'] = order
    return {'infrastructure_graph': infrastructure_graph}


def estimate_total_cost(selected_technologies, infrastructure_graph):
    # Compute levelized costs for selected technology for each node
    for node_id, node_d in infrastructure_graph.nodes_iter(data=True):
        if 'name' not in node_d:
            continue  # We have a fake node
        best_standalone_cost = float('inf')
        best_standalone_technology = 'grid'
        discounted_consumption = node_d['discounted_consumption_in_kwh']
        for technology in selected_technologies:
            discounted_cost = node_d[
                technology + '_internal_discounted_cost'] + node_d[
                technology + '_external_discounted_cost']
            node_d[technology + '_local_discounted_cost'] = discounted_cost
            node_d[technology + '_local_levelized_cost_per_kwh_consumed'] = \
                divide_safely(discounted_cost, discounted_consumption, 0)
            if technology != 'grid' and discounted_cost < best_standalone_cost:
                best_standalone_cost = discounted_cost
                best_standalone_technology = technology
        if infrastructure_graph.edge[node_id]:
            proposed_technology = 'grid'
        else:
            proposed_technology = best_standalone_technology
            node_d['grid_local_discounted_cost'] = ''
            node_d['grid_local_levelized_cost_per_kwh_consumed'] = ''
        node_d['proposed_technology'] = proposed_technology
        node_d['proposed_cost_per_connection'] = divide_safely(
            node_d[proposed_technology + '_local_discounted_cost'],
            node_d['final_connection_count'], 0)

    # Compute levelized costs for selected technology across all nodes
    count_by_technology = {x: 0 for x in selected_technologies}
    discounted_cost_by_technology = OrderedDefaultDict(int)
    discounted_consumption_by_technology = OrderedDefaultDict(int)
    for node_id, node_d in infrastructure_graph.nodes_iter(data=True):
        if 'name' not in node_d:
            continue  # We have a fake node
        technology = node_d['proposed_technology']
        count_by_technology[technology] += 1
        discounted_cost_by_technology[technology] += node_d[
            technology + '_local_discounted_cost']
        discounted_consumption_by_technology[technology] += node_d[
            'discounted_consumption_in_kwh']
    levelized_cost_by_technology = OrderedDict()
    for technology in selected_technologies:
        discounted_cost = discounted_cost_by_technology[
            technology]
        discounted_consumption = discounted_consumption_by_technology[
            technology]
        levelized_cost_by_technology[technology] = divide_safely(
            discounted_cost, discounted_consumption, 0)
    return {
        'count_by_technology': count_by_technology,
        'discounted_cost_by_technology': discounted_cost_by_technology,
        'levelized_cost_by_technology': levelized_cost_by_technology,
    }


MAIN_FUNCTIONS = [
    estimate_population,
    estimate_consumption_from_connection_type,
    estimate_consumption_profile,
    estimate_peak_demand,
    estimate_internal_cost_by_technology,
    estimate_grid_mv_line_budget,
    assemble_total_mv_line_network,
    sequence_total_mv_line_network,
    estimate_external_cost_by_technology,
    estimate_total_cost,
]
COLORS = 'bgrcmykw'
NORMALIZED_NAME_BY_COLUMN_NAME = {
    'installation labor and material cost': 'installation_lm_cost',
    'maintenance labor and material cost per year':
        'maintenance_lm_cost_per_year',
}
VARIABLE_NAMES_PATH = join('templates', basename(
    __file__).replace('.py', '').replace('_', '-'), 'columns.txt')
VARIABLE_NAMES = open(VARIABLE_NAMES_PATH).read().splitlines()


def run(g):
    try:
        g = normalize_arguments(g, NORMALIZED_NAME_BY_COLUMN_NAME)
    except InfrastructurePlanningError as e:
        raise e.__class__('%s.error = normalize_arguments : %s' % (
            e[0], e[1]))

    # Compute
    for f in MAIN_FUNCTIONS:
        if '_total_' in f.func_name:
            try:
                g.update(compute(f, g))
            except InfrastructurePlanningError as e:
                raise e.__class__('%s.error = %s : %s' % (
                    e[0], f.func_name, e[1]))
            continue
        graph = g['infrastructure_graph']
        for node_id, node_d in graph.nodes_iter(data=True):
            if 'name' not in node_d:
                continue  # We have a fake node
            l = merge_dictionaries(node_d, {
                'node_id': node_id,
                'local_overrides': dict(g['demand_point_table'].ix[node_id])})
            try:
                node_d.update(compute(f, l, g))
            except InfrastructurePlanningError as e:
                raise e.__class__('%s.error = %s : %s : %s' % (
                    e[0], l['name'].encode('utf-8'), f.func_name, e[1]))
    ls = [node_d for node_id, node_d in g[
        'infrastructure_graph'
    ].nodes_iter(data=True) if 'name' in node_d]  # Exclude fake nodes

    # Save
    target_folder = g['target_folder']
    summary_folder = make_folder(join(target_folder, 'summary'))
    save_summary(summary_folder, ls, g, VARIABLE_NAMES)
    save_glossary(summary_folder, ls, g)

    # Prepare summaries
    d = OrderedDict()
    graph = g['infrastructure_graph']
    # TODO: Use JSON after we convert pandas series into dictionaries
    write_gpickle(graph, join(target_folder, 'infrastructure_graph.pkl'))

    # Map
    technologies = g['selected_technologies']
    color_by_technology = {
        technology: COLORS[i] for i, technology in enumerate(technologies)
    }
    columns = [
        'Name',
        'Peak Demand (kW)',
        'Proposed MV Line Length (m)',
        'Proposed Technology',
        'Levelized Cost Per kWh Consumed',
        'Connection Order',
        'WKT',
        'FillColor',
        'RadiusInPixelsRange5-10',
    ]
    rows = []
    for node_id, node_d in graph.nodes_iter(data=True):
        if 'name' not in node_d:
            continue  # Exclude fake nodes
        longitude, latitude = node_d['longitude'], node_d['latitude']
        technology = node_d['proposed_technology']
        rows.append({
            'Name': node_d['name'],
            'Peak Demand (kW)': node_d['peak_demand_in_kw'],
            'Proposed MV Line Length (m)': node_d[
                'grid_mv_line_adjusted_length_in_meters'],
            'Proposed Technology': format_technology(technology),
            'Levelized Cost Per kWh Consumed': node_d[
                technology + '_local_levelized_cost_per_kwh_consumed'],
            'Connection Order': node_d.get('order', ''),
            'WKT': Point(latitude, longitude).wkt,
            'FillColor': color_by_technology[technology],
            'RadiusInPixelsRange5-10': node_d['peak_demand_in_kw'],
        })
    for node1_id, node2_id, edge_d in graph.edges_iter(data=True):
        node1_d, node2_d = graph.node[node1_id], graph.node[node2_id]
        name = 'From %s to %s' % (
            node1_d.get('name', 'the grid'),
            node2_d.get('name', 'the grid'))
        peak_demand = max(
            node1_d['peak_demand_in_kw'],
            node2_d['peak_demand_in_kw'])
        line_length = edge_d['grid_mv_line_adjusted_length_in_meters']
        geometry_wkt = LineString([
            (node1_d['latitude'], node1_d['longitude']),
            (node2_d['latitude'], node2_d['longitude']),
        ])
        rows.append({
            'Name': name,
            'Peak Demand (kW)': peak_demand,
            'Proposed MV Line Length (m)': line_length,
            'Proposed Technology': 'Grid',
            'WKT': geometry_wkt,
            'FillColor': color_by_technology['grid'],
        })
    if 'grid_mv_line_geotable' in g:
        for geometry_wkt in g['grid_mv_line_geotable']['wkt']:
            rows.append({
                'Name': '(Existing MV Line)',
                'Proposed Technology': 'grid',
                'WKT': geometry_wkt,
                'FillColor': color_by_technology['grid'],
            })
    infrastructure_geotable_path = join(
        target_folder, 'infrastructure_map.csv')
    DataFrame(rows)[columns].to_csv(infrastructure_geotable_path, index=False)
    d['infrastructure_streets_satellite_geotable_path'] = \
        infrastructure_geotable_path

    # Show executive summary
    keys = [
        'discounted_cost_by_technology',
        'levelized_cost_by_technology',
        'count_by_technology',
    ]
    table = concat((Series(g[key]) for key in keys), axis=1)
    table.index.name = 'Technology'
    table.index = [format_technology(x) for x in table.index]
    table.columns = [
        'Discounted Cost', 'Levelized Cost Per kWh Consumed', 'Count']
    table_path = join(target_folder, 'executive_summary.csv')
    table.to_csv(table_path)
    d['executive_summary_table_path'] = table_path
    # Show edge summary
    rows = []
    for node1_id, node2_id, edge_d in graph.edges_iter(data=True):
        node1_d = graph.node[node1_id]
        node2_d = graph.node[node2_id]
        name = 'From %s to %s' % (
            node1_d.get('name', 'the grid'),
            node2_d.get('name', 'the grid'))
        line_length = edge_d['grid_mv_line_adjusted_length_in_meters']
        discounted_cost = edge_d['grid_mv_line_discounted_cost']
        rows.append([name, line_length, discounted_cost])
    table_path = join(target_folder, 'grid_mv_line.csv')
    DataFrame(rows, columns=[
        'Name', 'Length (m)', 'Discounted Cost']).sort_values(
        'Length (m)',
    ).to_csv(table_path, index=False)
    d['grid_mv_line_table_path'] = table_path
    # Show node summary
    rows = []
    for node_id, node_d in graph.nodes_iter(data=True):
        if 'name' not in node_d:
            continue  # We have a fake node
        columns = [node_d['name'], node_d.get('order', '')]
        columns.extend(node_d[
            x + '_local_levelized_cost_per_kwh_consumed'
        ] for x in technologies)
        columns.append(format_technology(node_d['proposed_technology']))
        rows.append(columns)
    table_path = join(target_folder, 'levelized_cost_by_technology.csv')
    DataFrame(rows, columns=[
        'Name', 'Connection Order',
    ] + [
        format_technology(x) for x in technologies
    ] + ['Proposed Technology']).sort_values(
        'Connection Order',
    ).to_csv(table_path, index=False)
    d['levelized_cost_by_technology_table_path'] = table_path

    return d


def normalize_arguments(g, normalized_name_by_column_name):
    for k, v in g.items():
        if not hasattr(v, 'columns'):
            continue
        v.columns = normalize_column_names(
            v.columns, normalized_name_by_column_name)
    for normalize_argument in [
            normalize_demand_point_table,
            normalize_connection_type_table,
            normalize_grid_mv_line_geotable]:
        g.update(compute(normalize_argument, g))
    g['infrastructure_graph'] = get_graph_from_table(g['demand_point_table'])
    return g


def normalize_column_names(column_names, normalized_name_by_column_name):
    'Translate each column name into lowercase_english_with_underscores'
    normalized_names = []
    for column_name in column_names:
        column_name = column_name.lower()
        try:
            column_name = normalized_name_by_column_name[column_name]
        except KeyError:
            column_name = column_name.replace(' ', '_')
        normalized_names.append(column_name)
    return normalized_names


def normalize_demand_point_table(demand_point_table):
    if 'year' in demand_point_table.columns:
        # Rename year to population_year
        demand_point_table = demand_point_table.rename(columns={
            'year': 'population_year'})
    if 'population_year' in demand_point_table.columns:
        # TODO: Convert rows across multiple years into x_by_year
        # Use most recent population_year if there are many population_years
        demand_point_table = demand_point_table.sort_values(
            'population_year').groupby('name').last().reset_index()
    return {'demand_point_table': demand_point_table}


def normalize_connection_type_table(connection_type_table):
    connection_type_table['connection_type'] = connection_type_table[
        'connection_type'].apply(lambda x: x.lower().replace(' ', '_'))
    return {'connection_type_table': connection_type_table}


def normalize_grid_mv_line_geotable(grid_mv_line_geotable, demand_point_table):
    'Make sure that grid mv lines use (latitude, longitude) coordinate order'
    geometries = [wkt.loads(x) for x in grid_mv_line_geotable['wkt']]
    if geometries:
        regular = tuple(GeometryCollection(geometries).centroid.coords[0])[:2]
        flipped = regular[1], regular[0]
        reference = tuple(demand_point_table[['latitude', 'longitude']].mean())
        # If the flipped coordinates are closer,
        if get_distance(reference, flipped) < get_distance(reference, regular):
            # Flip coordinates to get (latitude, longitude) coordinate order
            for line in geometries:
                line.coords = [parsers.flip_xy(xyz) for xyz in line.coords]
            # ISO 6709 specifies (latitude, longitude) coordinate order
            grid_mv_line_geotable['wkt'] = [x.wkt for x in geometries]
    return {'grid_mv_line_geotable': grid_mv_line_geotable}


def save_summary(target_folder, ls, g, variable_names):
    keys = []
    for x in g['demand_point_table'].columns:
        if x in variable_names:
            continue
        keys.append(x)
    if len(keys) > 1:
        keys.append('')
    for x in variable_names:
        keys.append(x)
    table = get_table_from_variables(ls, g, keys)
    table.to_csv(join(target_folder, 'costs.csv'))
    example_table = table.reset_index().groupby(
        'proposed technology').first().reset_index().transpose()
    example_table.to_csv(join(target_folder, 'examples.csv'), header=False)


def save_glossary(target_folder, ls, g):
    l = ls[0] if len(ls) > 1 else {}

    selected_keys = []
    for key in sorted(set(l.keys() + g.keys())):
        value = l.get(key, g.get(key))
        if hasattr(value, '__iter__'):
            continue
        selected_keys.append(key)
    selected_keys.remove('target_folder')

    table = get_table_from_variables(ls, g, selected_keys)
    if not len(table):
        return
    table.ix[table.index[0]].to_csv(join(target_folder, 'glossary.csv'))


def format_technology(x):
    return x.replace('_', ' ').title()


def save_shapefile(target_path, geotable):
    # TODO: Save extra attributes
    geometries = [wkt.loads(x) for x in geotable['wkt']]
    # Shapefiles expect (x, y) or (longitude, latitude) coordinate order
    for geometry in geometries:
        geometry.coords = [parsers.flip_xy(xyz) for xyz in geometry.coords]
    geometryIO.save(target_path, geometryIO.proj4LL, geometries)
    return target_path


def load_arguments(value_by_key):
    configuration_path = value_by_key.pop('configuration_path')
    source_folder = value_by_key.pop('source_folder')
    g = json.load(open(configuration_path)) if configuration_path else {}
    # Command-line arguments override configuration arguments
    for k, v in value_by_key.items():
        if v is None:
            continue
        g[k] = v
    # Resolve relative paths using source_folder
    if source_folder:
        for k, v in g.items():
            if k.endswith('_path') and v and not isabs(v):
                g[k] = join(source_folder, v)
    return g


def save_arguments(g, script_path):
    d = g.copy()
    target_folder = d.pop('target_folder')
    if not target_folder:
        target_folder = make_enumerated_folder_for(script_path)
    arguments_folder = make_folder(join(target_folder, 'arguments'))
    for k, v in d.items():
        if not k.endswith('_path'):
            continue
        file_name = _get_argument_file_name(k, v)
        # Save a copy of each file
        shutil.copy(v, join(arguments_folder, file_name))
        # Make the reference point to the local copy
        d[k] = file_name
    # Save global arguments
    json.dump(d, open(join(arguments_folder, 'arguments.json'), 'w'))
    g['target_folder'] = target_folder


def load_files(g):
    file_key_pattern = re.compile(r'(.*)_(\w+)_path')
    file_value_by_name = {}
    for k, v in g.items():
        try:
            key_base, key_type = file_key_pattern.match(k).groups()
        except AttributeError:
            continue
        try:
            if key_type == 'text':
                name = key_base
                value = parsers.load_text(v)
            elif key_type == 'table':
                name = key_base + '_table'
                value = parsers.load_table(v)
            elif key_type == 'geotable':
                name = key_base + '_geotable'
                value = parsers.load_geotable(v)
            else:
                continue
        except UnsupportedFormat as e:
            raise e.__class__('%s.error = %s : load_files : %s' % (k, e[0]))
        file_value_by_name[name] = value
    return merge_dictionaries(g, file_value_by_name)


def _get_argument_file_name(k, v):
    file_base = k
    file_base = file_base.replace('_geotable_path', 's')
    file_base = file_base.replace('_table_path', 's')
    file_base = file_base.replace('_text_path', '')
    file_base = file_base.replace('_path', '')
    file_extension = splitext(v)[1]
    return file_base.replace('_', '-') + file_extension


if __name__ == '__main__':
    argument_parser = ArgumentParser()
    argument_parser.add_argument(
        'configuration_path',
        metavar='CONFIGURATION_PATH', nargs='?')
    argument_parser.add_argument(
        '-w', '--source_folder',
        metavar='FOLDER')
    argument_parser.add_argument(
        '-o', '--target_folder',
        metavar='FOLDER', type=make_folder)

    argument_parser.add_argument(
        '--selected_technologies_text_path',
        metavar='PATH')

    argument_parser.add_argument(
        '--financing_year',
        metavar='YEAR', type=int)
    argument_parser.add_argument(
        '--time_horizon_in_years',
        metavar='INTEGER', type=int)
    argument_parser.add_argument(
        '--discount_rate_as_percent_of_cash_flow_per_year',
        metavar='PERCENT', type=float)

    argument_parser.add_argument(
        '--demand_point_table_path',
        metavar='PATH')
    argument_parser.add_argument(
        '--population_year',
        metavar='YEAR', type=int)
    argument_parser.add_argument(
        '--population_growth_as_percent_of_population_per_year',
        metavar='FLOAT', type=float)

    argument_parser.add_argument(
        '--line_length_adjustment_factor',
        metavar='FLOAT', type=float)
    argument_parser.add_argument(
        '--average_distance_between_buildings_in_meters',
        metavar='FLOAT', type=float)
    argument_parser.add_argument(
        '--peak_hours_of_sun_per_year',
        metavar='FLOAT', type=float)

    argument_parser.add_argument(
        '--connection_type_table_path',
        metavar='PATH')
    argument_parser.add_argument(
        '--number_of_people_per_household',
        metavar='FLOAT', type=float)
    argument_parser.add_argument(
        '--consumption_during_peak_hours_as_percent_of_total_consumption',
        metavar='PERCENT', type=float)
    argument_parser.add_argument(
        '--peak_hours_of_consumption_per_year',
        metavar='FLOAT', type=float)

    argument_parser.add_argument(
        '--grid_electricity_production_cost_per_kwh',
        metavar='FLOAT', type=float)
    argument_parser.add_argument(
        '--grid_system_loss_as_percent_of_total_production',
        metavar='PERCENT', type=float)
    argument_parser.add_argument(
        '--grid_mv_network_minimum_point_count',
        metavar='INTEGER', type=int)
    argument_parser.add_argument(
        '--grid_mv_line_geotable_path',
        metavar='PATH')
    argument_parser.add_argument(
        '--grid_mv_line_installation_lm_cost_per_meter',
        metavar='FLOAT', type=float)
    argument_parser.add_argument(
        '--grid_mv_line_maintenance_lm_cost_per_meter_per_year',
        metavar='FLOAT', type=float)
    argument_parser.add_argument(
        '--grid_mv_line_lifetime_in_years',
        metavar='FLOAT', type=float)
    argument_parser.add_argument(
        '--grid_mv_transformer_load_power_factor',
        metavar='FLOAT', type=float)
    argument_parser.add_argument(
        '--grid_mv_transformer_table_path',
        metavar='PATH')
    argument_parser.add_argument(
        '--grid_lv_line_installation_lm_cost_per_meter',
        metavar='FLOAT', type=float)
    argument_parser.add_argument(
        '--grid_lv_line_maintenance_lm_cost_per_meter_per_year',
        metavar='FLOAT', type=float)
    argument_parser.add_argument(
        '--grid_lv_line_lifetime_in_years',
        metavar='FLOAT', type=float)
    argument_parser.add_argument(
        '--grid_lv_connection_installation_lm_cost_per_connection',
        metavar='FLOAT', type=float)
    argument_parser.add_argument(
        '--grid_lv_connection_maintenance_lm_cost_per_connection_per_year',
        metavar='FLOAT', type=float)
    argument_parser.add_argument(
        '--grid_lv_connection_lifetime_in_years',
        metavar='FLOAT', type=float)

    argument_parser.add_argument(
        '--diesel_mini_grid_system_loss_as_percent_of_total_production',
        metavar='PERCENT', type=float)
    argument_parser.add_argument(
        '--diesel_mini_grid_generator_table_path',
        metavar='PATH')
    argument_parser.add_argument(
        '--diesel_mini_grid_generator_minimum_hours_of_production_per_year',
        metavar='FLOAT', type=float)
    argument_parser.add_argument(
        '--diesel_mini_grid_generator_fuel_liters_consumed_per_kwh',
        metavar='FLOAT', type=float)
    argument_parser.add_argument(
        '--diesel_mini_grid_fuel_cost_per_liter',
        metavar='FLOAT', type=float)
    argument_parser.add_argument(
        '--diesel_mini_grid_lv_line_installation_lm_cost_per_meter',
        metavar='FLOAT', type=float)
    argument_parser.add_argument(
        '--diesel_mini_grid_lv_line_maintenance_lm_cost_per_meter_per_year',
        metavar='FLOAT', type=float)
    argument_parser.add_argument(
        '--diesel_mini_grid_lv_line_lifetime_in_years',
        metavar='FLOAT', type=float)
    argument_parser.add_argument(
        '--diesel_mini_grid_lv_connection_installation_lm_cost_per_connection',
        metavar='FLOAT', type=float)
    argument_parser.add_argument(
        '--diesel_mini_grid_lv_connection_maintenance_lm_cost_per_connection_per_year',  # noqa
        metavar='FLOAT', type=float)
    argument_parser.add_argument(
        '--diesel_mini_grid_lv_connection_lifetime_in_years',
        metavar='FLOAT', type=float)

    argument_parser.add_argument(
        '--solar_home_system_loss_as_percent_of_total_production',
        metavar='PERCENT', type=float)
    argument_parser.add_argument(
        '--solar_home_panel_table_path',
        metavar='PATH')
    argument_parser.add_argument(
        '--solar_home_battery_kwh_per_panel_kw',
        metavar='FLOAT', type=float)
    argument_parser.add_argument(
        '--solar_home_battery_installation_lm_cost_per_battery_kwh',
        metavar='FLOAT', type=float)
    argument_parser.add_argument(
        '--solar_home_battery_maintenance_lm_cost_per_kwh_per_year',
        metavar='FLOAT', type=float)
    argument_parser.add_argument(
        '--solar_home_battery_lifetime_in_years',
        metavar='FLOAT', type=float)
    argument_parser.add_argument(
        '--solar_home_balance_installation_lm_cost_per_panel_kw',
        metavar='FLOAT', type=float)
    argument_parser.add_argument(
        '--solar_home_balance_maintenance_lm_cost_per_panel_kw_per_year',
        metavar='FLOAT', type=float)
    argument_parser.add_argument(
        '--solar_home_balance_lifetime_in_years',
        metavar='FLOAT', type=float)

    argument_parser.add_argument(
        '--solar_mini_grid_system_loss_as_percent_of_total_production',
        metavar='PERCENT', type=float)
    argument_parser.add_argument(
        '--solar_mini_grid_panel_table_path',
        metavar='PATH')
    argument_parser.add_argument(
        '--solar_mini_grid_battery_kwh_per_panel_kw',
        metavar='FLOAT', type=float)
    argument_parser.add_argument(
        '--solar_mini_grid_battery_installation_lm_cost_per_battery_kwh',
        metavar='FLOAT', type=float)
    argument_parser.add_argument(
        '--solar_mini_grid_battery_maintenance_lm_cost_per_kwh_per_year',
        metavar='FLOAT', type=float)
    argument_parser.add_argument(
        '--solar_mini_grid_battery_lifetime_in_years',
        metavar='FLOAT', type=float)
    argument_parser.add_argument(
        '--solar_mini_grid_balance_installation_lm_cost_per_panel_kw',
        metavar='FLOAT', type=float)
    argument_parser.add_argument(
        '--solar_mini_grid_balance_maintenance_lm_cost_per_panel_kw_per_year',
        metavar='FLOAT', type=float)
    argument_parser.add_argument(
        '--solar_mini_grid_balance_lifetime_in_years',
        metavar='FLOAT', type=float)
    argument_parser.add_argument(
        '--solar_mini_grid_lv_line_installation_lm_cost_per_meter',
        metavar='FLOAT', type=float)
    argument_parser.add_argument(
        '--solar_mini_grid_lv_line_maintenance_lm_cost_per_meter_per_year',
        metavar='FLOAT', type=float)
    argument_parser.add_argument(
        '--solar_mini_grid_lv_line_lifetime_in_years',
        metavar='FLOAT', type=float)
    argument_parser.add_argument(
        '--solar_mini_grid_lv_connection_installation_lm_cost_per_connection',
        metavar='FLOAT', type=float)
    argument_parser.add_argument(
        '--solar_mini_grid_lv_connection_maintenance_lm_cost_per_connection_per_year',  # noqa
        metavar='FLOAT', type=float)
    argument_parser.add_argument(
        '--solar_mini_grid_lv_connection_lifetime_in_years',
        metavar='FLOAT', type=float)

    args = argument_parser.parse_args()
    g = load_arguments(args.__dict__)
    save_arguments(g, __file__)
    try:
        g = load_files(g)
        d = run(g)
    except InfrastructurePlanningError as e:
        exit(e[0])
    print(format_summary(d))
