import geometryIO
from collections import OrderedDict
from geopy import GoogleV3
from invisibleroads_macros.configuration import TerseArgumentParser
from invisibleroads_macros.disk import make_folder
from invisibleroads_macros.geometry import flip_geometry_coordinates
from invisibleroads_macros.iterable import OrderedDefaultDict
from invisibleroads_macros.math import divide_safely
from os.path import basename, join
from shapely import wkt

from infrastructure_planning.macros import (
    get_table_from_graph, load_and_run)
from infrastructure_planning.preprocessors import (
    normalize_demand_point_table,
    normalize_connection_type_table,
    normalize_grid_mv_transformer_table,
    normalize_diesel_mini_grid_generator_table,
    normalize_solar_home_panel_table,
    normalize_solar_mini_grid_panel_table,
    normalize_grid_mv_line_geotable)

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
from sequencer import NetworkPlan, Sequencer

from estimate_grid_mv_line_budget_in_meters import (
    add_arguments_for_estimate_population)


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


COLORS = 'bgrcmykw'
VARIABLE_NAMES_PATH = join('templates', basename(
    __file__).replace('.py', '').replace('_', '-'), 'columns.txt')
VARIABLE_NAMES = open(VARIABLE_NAMES_PATH).read().splitlines()


def save_shapefile(target_path, geotable):
    # TODO: Save extra attributes
    geometries = [wkt.loads(x) for x in geotable['wkt']]
    # Shapefiles expect (x, y) or (longitude, latitude) coordinate order
    flipped_geometries = flip_geometry_coordinates(geometries)
    geometryIO.save(target_path, geometryIO.proj4LL, flipped_geometries)
    return target_path


if __name__ == '__main__':
    x = TerseArgumentParser()
    add_arguments_for_estimate_population(x)

    x.add_argument(
        'configuration_path',
        metavar='CONFIGURATION_PATH', nargs='?')
    x.add_argument(
        '-w', '--source_folder',
        metavar='FOLDER')
    x.add_argument(
        '-o', '--target_folder',
        metavar='FOLDER', type=make_folder)

    x.add_argument(
        '--selected_technologies_text_path',
        metavar='PATH')

    x.add_argument(
        '--discount_rate_as_percent_of_cash_flow_per_year',
        metavar='PERCENT', type=float)

    x.add_argument(
        '--line_length_adjustment_factor',
        metavar='FLOAT', type=float)
    x.add_argument(
        '--average_distance_between_buildings_in_meters',
        metavar='FLOAT', type=float)
    x.add_argument(
        '--peak_hours_of_sun_per_year',
        metavar='FLOAT', type=float)

    x.add_argument(
        '--connection_type_table_path',
        metavar='PATH')
    x.add_argument(
        '--number_of_people_per_household',
        metavar='FLOAT', type=float)
    x.add_argument(
        '--consumption_during_peak_hours_as_percent_of_total_consumption',
        metavar='PERCENT', type=float)
    x.add_argument(
        '--peak_hours_of_consumption_per_year',
        metavar='FLOAT', type=float)

    x.add_argument(
        '--grid_electricity_production_cost_per_kwh',
        metavar='FLOAT', type=float)
    x.add_argument(
        '--grid_system_loss_as_percent_of_total_production',
        metavar='PERCENT', type=float)
    x.add_argument(
        '--grid_mv_network_minimum_point_count',
        metavar='INTEGER', type=int)
    x.add_argument(
        '--grid_mv_line_geotable_path',
        metavar='PATH')
    x.add_argument(
        '--grid_mv_line_raw_cost_per_meter',
        metavar='FLOAT', type=float)
    x.add_argument(
        '--grid_mv_line_installation_cost_as_percent_of_raw_cost',
        metavar='FLOAT', type=float)
    x.add_argument(
        '--grid_mv_line_maintenance_cost_per_year_as_percent_of_raw_cost',
        metavar='FLOAT', type=float)
    x.add_argument(
        '--grid_mv_line_lifetime_in_years',
        metavar='FLOAT', type=float)
    x.add_argument(
        '--grid_mv_transformer_load_power_factor',
        metavar='FLOAT', type=float)
    x.add_argument(
        '--grid_mv_transformer_table_path',
        metavar='PATH')
    x.add_argument(
        '--grid_lv_line_raw_cost_per_meter',
        metavar='FLOAT', type=float)
    x.add_argument(
        '--grid_lv_line_installation_cost_as_percent_of_raw_cost',
        metavar='FLOAT', type=float)
    x.add_argument(
        '--grid_lv_line_maintenance_cost_per_year_as_percent_of_raw_cost',
        metavar='FLOAT', type=float)
    x.add_argument(
        '--grid_lv_line_lifetime_in_years',
        metavar='FLOAT', type=float)
    x.add_argument(
        '--grid_lv_connection_raw_cost',
        metavar='FLOAT', type=float)
    x.add_argument(
        '--grid_lv_connection_installation_cost_as_percent_of_raw_cost',
        metavar='FLOAT', type=float)
    x.add_argument(
        '--grid_lv_connection_maintenance_cost_per_year_as_percent_of_raw_cost',  # noqa
        metavar='FLOAT', type=float)
    x.add_argument(
        '--grid_lv_connection_lifetime_in_years',
        metavar='FLOAT', type=float)

    x.add_argument(
        '--diesel_mini_grid_system_loss_as_percent_of_total_production',
        metavar='PERCENT', type=float)
    x.add_argument(
        '--diesel_mini_grid_generator_table_path',
        metavar='PATH')
    x.add_argument(
        '--diesel_mini_grid_generator_minimum_hours_of_production_per_year',
        metavar='FLOAT', type=float)
    x.add_argument(
        '--diesel_mini_grid_generator_fuel_liters_consumed_per_kwh',
        metavar='FLOAT', type=float)
    x.add_argument(
        '--diesel_mini_grid_fuel_cost_per_liter',
        metavar='FLOAT', type=float)
    x.add_argument(
        '--diesel_mini_grid_lv_line_raw_cost_per_meter',
        metavar='FLOAT', type=float)
    x.add_argument(
        '--diesel_mini_grid_lv_line_installation_cost_as_percent_of_raw_cost',
        metavar='FLOAT', type=float)
    x.add_argument(
        '--diesel_mini_grid_lv_line_maintenance_cost_per_year_as_percent_of_raw_cost',  # noqa
        metavar='FLOAT', type=float)
    x.add_argument(
        '--diesel_mini_grid_lv_line_lifetime_in_years',
        metavar='FLOAT', type=float)
    x.add_argument(
        '--diesel_mini_grid_lv_connection_raw_cost',
        metavar='FLOAT', type=float)
    x.add_argument(
        '--diesel_mini_grid_lv_connection_installation_cost_as_percent_of_raw_cost',  # noqa
        metavar='FLOAT', type=float)
    x.add_argument(
        '--diesel_mini_grid_lv_connection_maintenance_cost_per_year_as_percent_of_raw_cost',  # noqa
        metavar='FLOAT', type=float)
    x.add_argument(
        '--diesel_mini_grid_lv_connection_lifetime_in_years',
        metavar='FLOAT', type=float)

    x.add_argument(
        '--solar_home_system_loss_as_percent_of_total_production',
        metavar='PERCENT', type=float)
    x.add_argument(
        '--solar_home_panel_table_path',
        metavar='PATH')
    x.add_argument(
        '--solar_home_battery_kwh_per_panel_kw',
        metavar='FLOAT', type=float)
    x.add_argument(
        '--solar_home_battery_raw_cost_per_battery_kwh',
        metavar='FLOAT', type=float)
    x.add_argument(
        '--solar_home_battery_installation_cost_as_percent_of_raw_cost',
        metavar='FLOAT', type=float)
    x.add_argument(
        '--solar_home_battery_maintenance_cost_per_year_as_percent_of_raw_cost',  # noqa
        metavar='FLOAT', type=float)
    x.add_argument(
        '--solar_home_battery_lifetime_in_years',
        metavar='FLOAT', type=float)
    x.add_argument(
        '--solar_home_balance_raw_cost_per_panel_kw',
        metavar='FLOAT', type=float)
    x.add_argument(
        '--solar_home_balance_installation_cost_as_percent_of_raw_cost',
        metavar='FLOAT', type=float)
    x.add_argument(
        '--solar_home_balance_maintenance_cost_per_year_as_percent_of_raw_cost',  # noqa
        metavar='FLOAT', type=float)
    x.add_argument(
        '--solar_home_balance_lifetime_in_years',
        metavar='FLOAT', type=float)

    x.add_argument(
        '--solar_mini_grid_system_loss_as_percent_of_total_production',
        metavar='PERCENT', type=float)
    x.add_argument(
        '--solar_mini_grid_panel_table_path',
        metavar='PATH')
    x.add_argument(
        '--solar_mini_grid_battery_kwh_per_panel_kw',
        metavar='FLOAT', type=float)
    x.add_argument(
        '--solar_mini_grid_battery_raw_cost_per_battery_kwh',
        metavar='FLOAT', type=float)
    x.add_argument(
        '--solar_mini_grid_battery_installation_cost_as_percent_of_raw_cost',
        metavar='FLOAT', type=float)
    x.add_argument(
        '--solar_mini_grid_battery_maintenance_cost_per_year_as_percent_of_raw_cost',  # noqa
        metavar='FLOAT', type=float)
    x.add_argument(
        '--solar_mini_grid_battery_lifetime_in_years',
        metavar='FLOAT', type=float)
    x.add_argument(
        '--solar_mini_grid_balance_raw_cost_per_panel_kw',
        metavar='FLOAT', type=float)
    x.add_argument(
        '--solar_mini_grid_balance_installation_cost_as_percent_of_raw_cost',
        metavar='FLOAT', type=float)
    x.add_argument(
        '--solar_mini_grid_balance_maintenance_cost_per_year_as_percent_of_raw_cost',  # noqa
        metavar='FLOAT', type=float)
    x.add_argument(
        '--solar_mini_grid_balance_lifetime_in_years',
        metavar='FLOAT', type=float)
    x.add_argument(
        '--solar_mini_grid_lv_line_raw_cost_per_meter',
        metavar='FLOAT', type=float)
    x.add_argument(
        '--solar_mini_grid_lv_line_installation_cost_as_percent_of_raw_cost',
        metavar='FLOAT', type=float)
    x.add_argument(
        '--solar_mini_grid_lv_line_maintenance_cost_per_year_as_percent_of_raw_cost',  # noqa
        metavar='FLOAT', type=float)
    x.add_argument(
        '--solar_mini_grid_lv_line_lifetime_in_years',
        metavar='FLOAT', type=float)
    x.add_argument(
        '--solar_mini_grid_lv_connection_raw_cost',
        metavar='FLOAT', type=float)
    x.add_argument(
        '--solar_mini_grid_lv_connection_installation_cost_as_percent_of_raw_cost',  # noqa
        metavar='FLOAT', type=float)
    x.add_argument(
        '--solar_mini_grid_lv_connection_maintenance_cost_per_year_as_percent_of_raw_cost',  # noqa
        metavar='FLOAT', type=float)
    x.add_argument(
        '--solar_mini_grid_lv_connection_lifetime_in_years',
        metavar='FLOAT', type=float)
    load_and_run([
        normalize_demand_point_table,
        normalize_connection_type_table,
        normalize_grid_mv_transformer_table,
        normalize_diesel_mini_grid_generator_table,
        normalize_solar_home_panel_table,
        normalize_solar_mini_grid_panel_table,
        normalize_grid_mv_line_geotable,
    ], [
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
    ], x)
