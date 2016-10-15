from invisibleroads_macros.disk import make_folder
from os.path import join
from pandas import DataFrame, Series, concat
from shapely.geometry import LineString, Point

from ..macros import save_summary


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


def save_total_summary(
        target_folder, infrastructure_graph, selected_technologies,
        **keywords):
    graph = infrastructure_graph
    g = keywords

    ls = [node_d for node_id, node_d in infrastructure_graph.cycle_nodes()]
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
    for node_id, node_d in graph.cycle_nodes():
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
    for node_id, node_d in graph.cycle_nodes():
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
