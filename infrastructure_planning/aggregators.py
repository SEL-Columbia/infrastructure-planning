from collections import OrderedDict
from invisibleroads_macros.disk import make_folder
from invisibleroads_macros.iterable import OrderedDefaultDict
from invisibleroads_macros.math import divide_safely
from os.path import join
from pandas import DataFrame, Series, concat
from shapely.geometry import LineString, Point

from networker.networker_runner import NetworkerRunner
from sequencer import NetworkPlan, Sequencer

from .macros import get_table_from_graph, save_shapefile, save_summary


VARIABLE_NAMES_TEXT = """\
latitude
longitude
population
final_connection_count
final_consumption_in_kwh_per_year
peak_demand_in_kw
proposed_technology
proposed_cost_per_connection
order

grid_local_levelized_cost_per_kwh_consumed
diesel_mini_grid_local_levelized_cost_per_kwh_consumed
solar_home_local_levelized_cost_per_kwh_consumed
solar_mini_grid_local_levelized_cost_per_kwh_consumed

grid_local_discounted_cost
diesel_mini_grid_local_discounted_cost
solar_home_local_discounted_cost
solar_mini_grid_local_discounted_cost

grid_external_discounted_cost
grid_mv_line_adjusted_budget_in_meters
grid_mv_line_adjusted_length_in_meters
grid_internal_discounted_cost
grid_mv_transformer_actual_system_capacity_in_kva
grid_mv_transformer_raw_cost
grid_mv_transformer_installation_cost
grid_mv_transformer_maintenance_cost_per_year
grid_mv_transformer_replacement_cost_per_year
grid_lv_connection_raw_cost
grid_lv_connection_installation_cost
grid_lv_connection_maintenance_cost_per_year
grid_lv_connection_replacement_cost_per_year
grid_lv_line_raw_cost
grid_lv_line_installation_cost
grid_lv_line_maintenance_cost_per_year
grid_lv_line_replacement_cost_per_year

diesel_mini_grid_internal_discounted_cost
diesel_mini_grid_generator_actual_system_capacity_in_kw
diesel_mini_grid_lv_connection_raw_cost
diesel_mini_grid_lv_connection_installation_cost
diesel_mini_grid_lv_connection_maintenance_cost_per_year
diesel_mini_grid_lv_connection_replacement_cost_per_year
diesel_mini_grid_lv_line_raw_cost
diesel_mini_grid_lv_line_installation_cost
diesel_mini_grid_lv_line_maintenance_cost_per_year
diesel_mini_grid_lv_line_replacement_cost_per_year

solar_home_internal_discounted_cost
solar_home_panel_actual_system_capacity_in_kw
solar_home_panel_raw_cost
solar_home_panel_installation_cost
solar_home_panel_maintenance_cost_per_year
solar_home_panel_replacement_cost_per_year
solar_home_balance_raw_cost
solar_home_balance_installation_cost
solar_home_balance_maintenance_cost_per_year
solar_home_balance_replacement_cost_per_year
solar_home_battery_raw_cost
solar_home_battery_installation_cost
solar_home_battery_maintenance_cost_per_year
solar_home_battery_replacement_cost_per_year

solar_mini_grid_internal_discounted_cost
solar_mini_grid_panel_actual_system_capacity_in_kw
solar_mini_grid_panel_raw_cost
solar_mini_grid_panel_installation_cost
solar_mini_grid_panel_maintenance_cost_per_year
solar_mini_grid_panel_replacement_cost_per_year
solar_mini_grid_balance_raw_cost
solar_mini_grid_balance_installation_cost
solar_mini_grid_balance_maintenance_cost_per_year
solar_mini_grid_balance_replacement_cost_per_year
solar_mini_grid_battery_raw_cost
solar_mini_grid_battery_installation_cost
solar_mini_grid_battery_maintenance_cost_per_year
solar_mini_grid_battery_replacement_cost_per_year
solar_mini_grid_lv_connection_raw_cost
solar_mini_grid_lv_connection_installation_cost
solar_mini_grid_lv_connection_maintenance_cost_per_year
solar_mini_grid_lv_connection_replacement_cost_per_year
solar_mini_grid_lv_line_raw_cost
solar_mini_grid_lv_line_installation_cost
solar_mini_grid_lv_line_maintenance_cost_per_year
solar_mini_grid_lv_line_replacement_cost_per_year
"""
VARIABLE_NAMES = VARIABLE_NAMES_TEXT.splitlines()


def assemble_total_mv_line_network(
        target_folder, infrastructure_graph, grid_mv_line_geotable,
        grid_mv_network_minimum_point_count):
    graph = infrastructure_graph
    node_table = get_table_from_graph(graph, [
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
        if node_id in graph:
            continue
        # Add fake nodes (I think that is what these are)
        longitude, latitude = msf.coords[node_id]
        graph.add_node(node_id, {
            'longitude': longitude,
            'latitude': latitude,
            'population': 0,
            'peak_demand_in_kw': 0,
        })
    graph.add_edges_from(msf.edges_iter())
    return {'infrastructure_graph': graph}


def sequence_total_mv_line_network(target_folder, infrastructure_graph):
    graph = infrastructure_graph
    if not graph.edges():
        return {}  # The network is empty and there is nothing to sequence
    node_table = get_table_from_graph(graph, [
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
        graph.node[node_id]['order'] = order
    return {'infrastructure_graph': graph}


def estimate_total_cost(infrastructure_graph, selected_technologies):
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


def save_total_summary(
        target_folder, infrastructure_graph, selected_technologies,
        **keywords):
    graph = infrastructure_graph
    g = keywords

    ls = [
        node_d for node_id, node_d in
        infrastructure_graph.nodes_iter(data=True)
        if 'name' in node_d]  # Exclude fake nodes

    summary_folder = make_folder(join(target_folder, 'summary'))
    save_summary(summary_folder, ls, g, VARIABLE_NAMES)

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

    print('executive_summary_table_path = %s' % table_path)

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

    print('grid_mv_line_table_path = %s' % table_path)

    # Show node summary
    rows = []
    for node_id, node_d in graph.nodes_iter(data=True):
        if 'name' not in node_d:
            continue  # We have a fake node
        columns = [node_d['name'], node_d.get('order', '')]
        columns.extend(node_d[
            x + '_local_levelized_cost_per_kwh_consumed'
        ] for x in selected_technologies)
        columns.append(format_technology(node_d['proposed_technology']))
        rows.append(columns)
    table_path = join(target_folder, 'levelized_cost_by_technology.csv')
    DataFrame(rows, columns=[
        'Name', 'Connection Order',
    ] + [
        format_technology(x) for x in selected_technologies
    ] + ['Proposed Technology']).sort_values(
        'Connection Order',
    ).to_csv(table_path, index=False)
    print('levelized_cost_by_technology_table_path = %s' % table_path)


def save_total_map(
        target_folder, infrastructure_graph, selected_technologies,
        grid_mv_line_geotable):
    graph = infrastructure_graph
    colors = 'bgrcmykw'
    color_by_technology = {
        x: colors[i] for i, x in enumerate(selected_technologies)
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
    for geometry_wkt in grid_mv_line_geotable['wkt']:
        rows.append({
            'Name': '(Existing MV Line)',
            'Proposed Technology': 'grid',
            'WKT': geometry_wkt,
            'FillColor': color_by_technology['grid'],
        })
    target_path = join(target_folder, 'infrastructure_map.csv')
    DataFrame(rows)[columns].to_csv(target_path, index=False)
    print('infrastructure_streets_satellite_geotable_path = %s' % target_path)


def format_technology(x):
    return x.replace('_', ' ').title()
