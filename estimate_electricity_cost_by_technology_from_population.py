import geometryIO
from argparse import ArgumentParser
from collections import OrderedDict
from geopy import GoogleV3
from geopy.distance import vincenty as get_distance
from invisibleroads_macros.disk import make_enumerated_folder_for, make_folder
from invisibleroads_macros.iterable import (
    OrderedDefaultDict, merge_dictionaries)
from invisibleroads_macros.log import format_summary
from networkx import write_gpickle
from os.path import basename, join
from pandas import DataFrame, Series, concat, read_csv
from shapely.geometry import GeometryCollection, LineString, Point
from shapely import wkt

from infrastructure_planning.exceptions import InfrastructurePlanningError
from infrastructure_planning.macros import (
    compute, get_graph_from_table, get_table_from_graph,
    get_table_from_variables)

from infrastructure_planning.demography.exponential import estimate_population
from infrastructure_planning.electricity.consumption.linear import (
    estimate_consumption)
from infrastructure_planning.electricity.demand import estimate_peak_demand
from infrastructure_planning.electricity.cost import (
    estimate_internal_cost_by_technology, estimate_external_cost_by_technology)
from infrastructure_planning.electricity.cost.grid import (
    estimate_mv_line_budget)
from networker.networker_runner import NetworkerRunner
from sequencer import NetworkPlan
from sequencer.Models import EnergyMaximizeReturn


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
        'longitude', 'latitude', 'grid_mv_line_adjusted_budget'])
    node_table_path = join(target_folder, 'nodes-networker.csv')
    node_table.to_csv(node_table_path)
    nwk_settings = {
        'demand_nodes': {
            'filename': node_table_path,
            'x_column': 'longitude',
            'y_column': 'latitude',
            'budget_column': 'grid_mv_line_adjusted_budget',
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
    nwp = NetworkPlan(
        edge_shapefile_path, node_table_path, prioritize='population')
    model = EnergyMaximizeReturn(nwp)
    model.sequence()
    order_series = model.output_frame['Sequence..Far.sighted.sequence']
    for index, order in order_series.iteritems():
        node_id = model.output_frame['Unnamed..0'][index]
        infrastructure_graph.node[node_id]['order'] = order
    return {'infrastructure_graph': infrastructure_graph}


def estimate_total_cost(selected_technologies, infrastructure_graph):
    for node_id, node_d in infrastructure_graph.nodes_iter(data=True):
        if 'name' not in node_d:
            continue  # We have a fake node
        best_standalone_cost = float('inf')
        best_standalone_technology = 'grid'
        for technology in selected_technologies:
            discounted_cost = node_d[
                technology + '_internal_discounted_cost'] + node_d[
                technology + '_external_discounted_cost']
            discounted_production = node_d[
                technology + '_electricity_discounted_production_in_kwh']
            levelized_cost = discounted_cost / float(
                discounted_production) if discounted_production else 0
            node_d[technology + '_total_discounted_cost'] = discounted_cost
            node_d[technology + '_total_levelized_cost'] = levelized_cost
            if technology != 'grid' and discounted_cost < best_standalone_cost:
                best_standalone_cost = discounted_cost
                best_standalone_technology = technology
        if infrastructure_graph.edge[node_id]:
            proposed_technology = 'grid'
        else:
            proposed_technology = best_standalone_technology
            node_d['grid_total_discounted_cost'] = ''
            node_d['grid_total_levelized_cost'] = ''
        node_d['proposed_technology'] = proposed_technology
        node_d['proposed_cost_per_connection'] = node_d[
            proposed_technology + '_total_discounted_cost'] / float(node_d[
                'maximum_connection_count'])
    # Compute levelized costs for selected technology across all nodes
    count_by_technology = {x: 0 for x in selected_technologies}
    discounted_cost_by_technology = OrderedDefaultDict(int)
    discounted_production_by_technology = OrderedDefaultDict(int)
    for node_id, node_d in infrastructure_graph.nodes_iter(data=True):
        if 'name' not in node_d:
            continue  # We have a fake node
        technology = node_d['proposed_technology']
        count_by_technology[technology] += 1
        discounted_cost_by_technology[technology] += node_d[
            technology + '_total_discounted_cost']
        discounted_production_by_technology[technology] += node_d[
            technology + '_electricity_discounted_production_in_kwh']
    levelized_cost_by_technology = OrderedDict()
    for technology in selected_technologies:
        discounted_cost = discounted_cost_by_technology[
            technology]
        discounted_production = discounted_production_by_technology[
            technology]
        levelized_cost_by_technology[technology] = discounted_cost / float(
            discounted_production) if discounted_cost else 0
    return {
        'count_by_technology': count_by_technology,
        'discounted_cost_by_technology': discounted_cost_by_technology,
        'levelized_cost_by_technology': levelized_cost_by_technology,
    }


MAIN_FUNCTIONS = [
    estimate_population,
    estimate_consumption,
    estimate_peak_demand,
    estimate_internal_cost_by_technology,
    estimate_mv_line_budget,
    assemble_total_mv_line_network,
    sequence_total_mv_line_network,
    estimate_external_cost_by_technology,
    estimate_total_cost,
]
COLORS = 'bgrcmykw'
TABLE_NAMES = [
    'demand_point_table',
    'grid_mv_transformer_table',
    'diesel_mini_grid_generator_table',
    'solar_home_panel_table',
]
NORMALIZED_NAME_BY_COLUMN_NAME = {
    'capacity in kva': 'capacity_in_kva',
    'capacity in kw': 'capacity_in_kw',
    'installation labor and material cost': 'installation_lm_cost',
    'maintenance labor and material cost per year':
        'maintenance_lm_cost_per_year',
    'lifetime in years': 'lifetime_in_years'
}
VARIABLE_NAMES_PATH = join('templates', basename(
    __file__).replace('.py', '').replace('_', '-'), 'summary-columns.txt')
VARIABLE_NAMES = open(VARIABLE_NAMES_PATH).read().splitlines()


def run(target_folder, g):
    g = prepare_parameters(g, TABLE_NAMES, NORMALIZED_NAME_BY_COLUMN_NAME)

    # Compute
    for f in MAIN_FUNCTIONS:
        if '_total_' in f.func_name:
            try:
                g.update(compute(f, g))
            except InfrastructurePlanningError as e:
                exit('%s.error = %s : %s' % (e[0], f.func_name, e[1]))
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
                exit('%s.error = %s : %s : %s' % (
                    e[0], l['name'].encode('utf-8'), f.func_name, e[1]))
    ls = [node_d for node_id, node_d in g[
        'infrastructure_graph'
    ].nodes_iter(data=True) if 'name' in node_d]  # Exclude fake nodes

    # Save
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
        'Levelized Cost',
        'Connection Order',
        'WKT',
        'FillColor',
        'RadiusInPixelsRange2-8',
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
            'Levelized Cost': node_d[technology + '_total_levelized_cost'],
            'Connection Order': node_d.get('order', ''),
            'WKT': Point(latitude, longitude).wkt,
            'FillColor': color_by_technology[technology],
            'RadiusInPixelsRange2-8': node_d['peak_demand_in_kw'],
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
        for geometry_wkt in g['grid_mv_line_geotable']['WKT']:
            rows.append({
                'Name': '(Existing Grid)',
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
    table.columns = ['Discounted Cost', 'Levelized Cost', 'Count']
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
            x + '_total_levelized_cost'] for x in technologies)
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


def prepare_parameters(g, table_names, normalized_name_by_column_name):
    for table_name in table_names:
        table = g[table_name]
        table.columns = normalize_column_names(
            table.columns, normalized_name_by_column_name)
    for prepare_parameter in [
            prepare_demand_point_table,
            prepare_grid_mv_line_geotable]:
        g.update(compute(prepare_parameter, g))
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
            pass
        normalized_names.append(column_name)
    return normalized_names


def prepare_demand_point_table(demand_point_table):
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


def prepare_grid_mv_line_geotable(grid_mv_line_geotable, demand_point_table):
    'Make sure that grid mv lines use (latitude, longitude) coordinate order'
    geometries = [wkt.loads(x) for x in grid_mv_line_geotable['WKT']]
    if geometries:
        regular = tuple(GeometryCollection(geometries).centroid.coords[0])[:2]
        flipped = regular[1], regular[0]
        reference = tuple(demand_point_table[['latitude', 'longitude']].mean())
        # If the flipped coordinates are closer,
        if get_distance(reference, flipped) < get_distance(reference, regular):
            # Flip coordinates to get (latitude, longitude) coordinate order
            for line in geometries:
                line.coords = [flip_xy(xyz) for xyz in line.coords]
            # ISO 6709 specifies (latitude, longitude) coordinate order
            grid_mv_line_geotable['WKT'] = [x.wkt for x in geometries]
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
        'proposed_technology').first().reset_index().transpose()
    example_table.to_csv(join(target_folder, 'examples.csv'), header=False)


def save_glossary(target_folder, ls, g):
    l = ls[0] if len(ls) > 1 else {}

    keys = []
    keys.extend(l.keys())
    keys.extend(g.keys())
    keys.sort()

    selected_keys = []
    for key in keys:
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


def flip_xy(xyz):
    xyz = list(xyz)
    xyz[0], xyz[1] = xyz[1], xyz[0]
    return xyz


def save_shapefile(target_path, geotable):
    # TODO: Save extra attributes
    geometries = [wkt.loads(x) for x in geotable['WKT']]
    # Shapefiles expect (x, y) or (longitude, latitude) coordinate order
    for geometry in geometries:
        geometry.coords = [flip_xy(xyz) for xyz in geometry.coords]
    geometryIO.save(target_path, geometryIO.proj4LL, geometries)
    return target_path


if __name__ == '__main__':
    argument_parser = ArgumentParser()
    argument_parser.add_argument(
        '--target_folder',
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
        metavar='INTEGER', type=int)

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
        '--number_of_people_per_connection',
        metavar='FLOAT', type=float)
    argument_parser.add_argument(
        '--consumption_in_kwh_per_connection',
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

    args = argument_parser.parse_args()
    g = args.__dict__.copy()
    g['selected_technologies'] = open(g.pop(
        'selected_technologies_text_path')).read().split()
    g['demand_point_table'] = read_csv(g.pop('demand_point_table_path'))
    g['grid_mv_line_geotable'] = read_csv(g.pop('grid_mv_line_geotable_path'))
    g['grid_mv_transformer_table'] = read_csv(g.pop(
        'grid_mv_transformer_table_path'))
    g['diesel_mini_grid_generator_table'] = read_csv(g.pop(
        'diesel_mini_grid_generator_table_path'))
    g['solar_home_panel_table'] = read_csv(g.pop(
        'solar_home_panel_table_path'))
    d = run(args.target_folder or make_enumerated_folder_for(__file__), g)
    print(format_summary(d))
