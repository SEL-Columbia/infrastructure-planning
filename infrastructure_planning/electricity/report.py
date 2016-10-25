from invisibleroads_macros.disk import make_folder
from os.path import join
from pandas import DataFrame, Series, concat
from shapely.geometry import LineString, Point

from ..macros import get_table_from_variables


BASE_KEYS = """\
name
latitude
longitude
population
""".strip().splitlines()


FULL_KEYS = """\
proposed_technology
proposed_cost_per_connection
order
financing_year
time_horizon_in_years
discount_rate_as_percent_of_cash_flow_per_year
population_year
population_growth_as_percent_of_population_per_year
line_length_adjustment_factor
average_distance_between_buildings_in_meters
peak_hours_of_sun_per_year
number_of_people_per_household
final_population
final_connection_count
consumption_during_peak_hours_as_percent_of_total_consumption
peak_hours_of_consumption_per_year
peak_demand_in_kw
final_consumption_in_kwh_per_year
discounted_consumption_in_kwh
grid_electricity_production_cost_per_kwh
grid_system_loss_as_percent_of_total_production
grid_mv_network_minimum_point_count
grid_mv_line_raw_cost_per_meter
grid_mv_line_installation_cost_as_percent_of_raw_cost
grid_mv_line_installation_cost_per_meter
grid_mv_line_maintenance_cost_per_year_as_percent_of_raw_cost
grid_mv_line_maintenance_cost_per_meter_per_year
grid_mv_line_lifetime_in_years
grid_mv_line_replacement_cost_per_meter_per_year
grid_mv_line_final_cost_per_meter_per_year
grid_mv_line_discounted_cost_per_meter
grid_mv_line_adjusted_length_in_meters
grid_mv_line_adjusted_budget_in_meters
grid_mv_transformer_load_power_factor
grid_mv_transformer_actual_system_capacity_in_kva
grid_mv_transformer_raw_cost
grid_mv_transformer_installation_cost
grid_mv_transformer_maintenance_cost_per_year
grid_mv_transformer_replacement_cost_per_year
grid_lv_line_raw_cost_per_meter
grid_lv_line_raw_cost
grid_lv_line_installation_cost_as_percent_of_raw_cost
grid_lv_line_installation_cost
grid_lv_line_maintenance_cost_per_year_as_percent_of_raw_cost
grid_lv_line_maintenance_cost_per_year
grid_lv_line_lifetime_in_years
grid_lv_line_replacement_cost_per_year
grid_lv_connection_raw_cost
grid_lv_connection_installation_cost_as_percent_of_raw_cost
grid_lv_connection_installation_cost
grid_lv_connection_maintenance_cost_per_year_as_percent_of_raw_cost
grid_lv_connection_maintenance_cost_per_year
grid_lv_connection_lifetime_in_years
grid_lv_connection_replacement_cost_per_year
grid_final_electricity_production_in_kwh_per_year
grid_final_electricity_production_cost_per_year
grid_final_internal_distribution_cost_per_year
grid_final_external_distribution_cost_per_year
grid_internal_discounted_cost
grid_internal_levelized_cost_per_kwh_consumed
grid_external_discounted_cost
grid_local_initial_cost
grid_local_recurring_cost
grid_local_discounted_cost
grid_local_levelized_cost_per_kwh_consumed
diesel_mini_grid_system_loss_as_percent_of_total_production
diesel_mini_grid_fuel_cost_per_liter
diesel_mini_grid_generator_minimum_hours_of_production_per_year
diesel_mini_grid_generator_fuel_liters_consumed_per_kwh
diesel_mini_grid_generator_actual_system_capacity_in_kw
diesel_mini_grid_generator_raw_cost
diesel_mini_grid_generator_installation_cost
diesel_mini_grid_generator_maintenance_cost_per_year
diesel_mini_grid_generator_replacement_cost_per_year
diesel_mini_grid_lv_line_raw_cost_per_meter
diesel_mini_grid_lv_line_raw_cost
diesel_mini_grid_lv_line_installation_cost_as_percent_of_raw_cost
diesel_mini_grid_lv_line_installation_cost
diesel_mini_grid_lv_line_maintenance_cost_per_year_as_percent_of_raw_cost
diesel_mini_grid_lv_line_maintenance_cost_per_year
diesel_mini_grid_lv_line_lifetime_in_years
diesel_mini_grid_lv_line_replacement_cost_per_year
diesel_mini_grid_lv_connection_raw_cost
diesel_mini_grid_lv_connection_installation_cost_as_percent_of_raw_cost
diesel_mini_grid_lv_connection_installation_cost
diesel_mini_grid_lv_connection_maintenance_cost_per_year_as_percent_of_raw_cost
diesel_mini_grid_lv_connection_maintenance_cost_per_year
diesel_mini_grid_lv_connection_lifetime_in_years
diesel_mini_grid_lv_connection_replacement_cost_per_year
diesel_mini_grid_final_hours_of_production_per_year
diesel_mini_grid_final_fuel_cost_per_year
diesel_mini_grid_final_electricity_production_in_kwh_per_year
diesel_mini_grid_final_electricity_production_cost_per_year
diesel_mini_grid_final_internal_distribution_cost_per_year
diesel_mini_grid_final_external_distribution_cost_per_year
diesel_mini_grid_internal_discounted_cost
diesel_mini_grid_internal_levelized_cost_per_kwh_consumed
diesel_mini_grid_external_discounted_cost
diesel_mini_grid_local_initial_cost
diesel_mini_grid_local_recurring_cost
diesel_mini_grid_local_discounted_cost
diesel_mini_grid_local_levelized_cost_per_kwh_consumed
solar_home_system_loss_as_percent_of_total_production
solar_home_panel_actual_system_capacity_in_kw
solar_home_panel_raw_cost
solar_home_panel_installation_cost
solar_home_panel_maintenance_cost_per_year
solar_home_panel_replacement_cost_per_year
solar_home_battery_storage_in_kwh
solar_home_battery_kwh_per_panel_kw
solar_home_battery_raw_cost_per_battery_kwh
solar_home_battery_raw_cost
solar_home_battery_installation_cost_as_percent_of_raw_cost
solar_home_battery_installation_cost
solar_home_battery_maintenance_cost_per_year_as_percent_of_raw_cost
solar_home_battery_maintenance_cost_per_year
solar_home_battery_lifetime_in_years
solar_home_battery_replacement_cost_per_year
solar_home_balance_raw_cost_per_panel_kw
solar_home_balance_raw_cost
solar_home_balance_installation_cost_as_percent_of_raw_cost
solar_home_balance_installation_cost
solar_home_balance_maintenance_cost_per_year_as_percent_of_raw_cost
solar_home_balance_maintenance_cost_per_year
solar_home_balance_lifetime_in_years
solar_home_balance_replacement_cost_per_year
solar_home_final_electricity_production_in_kwh_per_year
solar_home_final_electricity_production_cost_per_year
solar_home_final_internal_distribution_cost_per_year
solar_home_final_external_distribution_cost_per_year
solar_home_internal_discounted_cost
solar_home_internal_levelized_cost_per_kwh_consumed
solar_home_external_discounted_cost
solar_home_local_initial_cost
solar_home_local_recurring_cost
solar_home_local_discounted_cost
solar_home_local_levelized_cost_per_kwh_consumed
solar_mini_grid_system_loss_as_percent_of_total_production
solar_mini_grid_panel_actual_system_capacity_in_kw
solar_mini_grid_panel_raw_cost
solar_mini_grid_panel_installation_cost
solar_mini_grid_panel_maintenance_cost_per_year
solar_mini_grid_panel_replacement_cost_per_year
solar_mini_grid_battery_storage_in_kwh
solar_mini_grid_battery_kwh_per_panel_kw
solar_mini_grid_battery_raw_cost_per_battery_kwh
solar_mini_grid_battery_raw_cost
solar_mini_grid_battery_installation_cost_as_percent_of_raw_cost
solar_mini_grid_battery_installation_cost
solar_mini_grid_battery_maintenance_cost_per_year_as_percent_of_raw_cost
solar_mini_grid_battery_maintenance_cost_per_year
solar_mini_grid_battery_lifetime_in_years
solar_mini_grid_battery_replacement_cost_per_year
solar_mini_grid_balance_raw_cost_per_panel_kw
solar_mini_grid_balance_raw_cost
solar_mini_grid_balance_installation_cost_as_percent_of_raw_cost
solar_mini_grid_balance_installation_cost
solar_mini_grid_balance_maintenance_cost_per_year_as_percent_of_raw_cost
solar_mini_grid_balance_maintenance_cost_per_year
solar_mini_grid_balance_lifetime_in_years
solar_mini_grid_balance_replacement_cost_per_year
solar_mini_grid_lv_line_raw_cost_per_meter
solar_mini_grid_lv_line_raw_cost
solar_mini_grid_lv_line_installation_cost_as_percent_of_raw_cost
solar_mini_grid_lv_line_installation_cost
solar_mini_grid_lv_line_maintenance_cost_per_year_as_percent_of_raw_cost
solar_mini_grid_lv_line_maintenance_cost_per_year
solar_mini_grid_lv_line_lifetime_in_years
solar_mini_grid_lv_line_replacement_cost_per_year
solar_mini_grid_lv_connection_raw_cost
solar_mini_grid_lv_connection_installation_cost_as_percent_of_raw_cost
solar_mini_grid_lv_connection_installation_cost
solar_mini_grid_lv_connection_maintenance_cost_per_year_as_percent_of_raw_cost
solar_mini_grid_lv_connection_maintenance_cost_per_year
solar_mini_grid_lv_connection_lifetime_in_years
solar_mini_grid_lv_connection_replacement_cost_per_year
solar_mini_grid_final_electricity_production_in_kwh_per_year
solar_mini_grid_final_electricity_production_cost_per_year
solar_mini_grid_final_internal_distribution_cost_per_year
solar_mini_grid_final_external_distribution_cost_per_year
solar_mini_grid_internal_discounted_cost
solar_mini_grid_internal_levelized_cost_per_kwh_consumed
solar_mini_grid_external_discounted_cost
solar_mini_grid_local_initial_cost
solar_mini_grid_local_recurring_cost
solar_mini_grid_local_discounted_cost
solar_mini_grid_local_levelized_cost_per_kwh_consumed
""".strip().splitlines()


SOME_KEYS = """\
final_population
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

grid_local_initial_cost
diesel_mini_grid_local_initial_cost
solar_home_local_initial_cost
solar_mini_grid_local_initial_cost

grid_local_recurring_cost
diesel_mini_grid_local_recurring_cost
solar_home_local_recurring_cost
solar_mini_grid_local_recurring_cost

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

diesel_mini_grid_external_discounted_cost
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

solar_home_external_discounted_cost
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

solar_mini_grid_external_discounted_cost
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
""".strip().splitlines()


def save_total_points(
        target_folder, infrastructure_graph, demand_point_table, **keywords):
    ls = [node_d for node_id, node_d in infrastructure_graph.cycle_nodes()]
    g = keywords

    properties_folder = make_folder(join(target_folder, 'properties'))

    t = get_table_from_variables(ls, g, keys=BASE_KEYS + [
        x for x in demand_point_table.columns if x not in BASE_KEYS + FULL_KEYS
    ] + FULL_KEYS)
    t_path = join(properties_folder, 'points.csv')
    t.to_csv(t_path)


def save_total_report_by_location(
        target_folder, infrastructure_graph, **keywords):
    ls = [node_d for node_id, node_d in infrastructure_graph.cycle_nodes()]
    g = keywords

    reports_folder = make_folder(join(target_folder, 'reports'))

    t = get_table_from_variables(ls, g, keys=BASE_KEYS + SOME_KEYS)
    t.columns = [format_column_name(x) for x in t.columns]
    t_path = join(reports_folder, 'report-by-location.csv')
    t.to_csv(t_path)

    table = t.reset_index().groupby(
        'proposed technology').first().reset_index().transpose()
    table_path = join(reports_folder, 'example-by-technology.csv')
    table.to_csv(table_path, header=False)


def save_total_summary_by_technology(
        target_folder, discounted_cost_by_technology,
        levelized_cost_by_technology, count_by_technology):
    t = concat([
        Series(discounted_cost_by_technology),
        Series(levelized_cost_by_technology),
        Series(count_by_technology),
    ], axis=1)
    t.index.name = 'Technology'
    t.index = [format_technology(x) for x in t.index]
    t.columns = [
        'Discounted Cost',
        'Levelized Cost Per kWh Consumed',
        'Count',
    ]

    reports_folder = make_folder(join(target_folder, 'reports'))
    t_path = join(reports_folder, 'summary-by-technology.csv')
    t.to_csv(t_path)
    print('summary_by_technology_table_path = %s' % t_path)


def save_total_summary_by_location(
        target_folder, infrastructure_graph, selected_technologies):
    rows = []
    for node_id, node_d in infrastructure_graph.cycle_nodes():
        xs = [node_d['name'], node_d.get('order', '')]
        xs.extend(node_d[
            x + '_local_levelized_cost_per_kwh_consumed'
        ] for x in selected_technologies)
        xs.append(format_technology(node_d['proposed_technology']))
        rows.append(xs)
    t = DataFrame(rows, columns=[
        'Name',
        'Connection Order',
    ] + [format_technology(x) for x in selected_technologies] + [
        'Proposed Technology',
    ]).sort_values('Connection Order')

    reports_folder = make_folder(join(target_folder, 'reports'))
    t_path = join(reports_folder, 'summary-by-location.csv')
    t.to_csv(t_path, index=False)
    print('summary_by_location_table_path = %s' % t_path)


def save_total_summary_by_grid_mv_line(target_folder, infrastructure_graph):
    rows = []
    for node1_id, node2_id, edge_d in infrastructure_graph.cycle_edges():
        node1_d = infrastructure_graph.node[node1_id]
        node2_d = infrastructure_graph.node[node2_id]
        name = 'From %s to %s' % (
            node1_d.get('name', 'the grid'),
            node2_d.get('name', 'the grid'))
        line_length = edge_d['grid_mv_line_adjusted_length_in_meters']
        discounted_cost = edge_d['grid_mv_line_discounted_cost']
        rows.append([name, line_length, discounted_cost])
    t = DataFrame(rows, columns=[
        'Name',
        'Length (m)',
        'Discounted Cost',
    ]).sort_values('Length (m)')

    reports_folder = make_folder(join(target_folder, 'reports'))
    t_path = join(reports_folder, 'summary-by-grid-mv-line.csv')
    t.to_csv(t_path, index=False)
    print('summary_by_grid_mv_line_table_path = %s' % t_path)


def save_total_map(
        target_folder, infrastructure_graph, selected_technologies,
        grid_mv_line_geotable):
    graph = infrastructure_graph
    colors = 'bgrcmykw'
    color_by_technology = {x: colors[i] for i, x in enumerate([
        'unelectrified'] + selected_technologies)}
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
        levelized_cost = node_d.get(
            technology + '_local_levelized_cost_per_kwh_consumed', 0)
        rows.append({
            'Name': node_d['name'],
            'Peak Demand (kW)': node_d['peak_demand_in_kw'],
            'Proposed MV Line Length (m)': node_d[
                'grid_mv_line_adjusted_length_in_meters'],
            'Proposed Technology': format_technology(technology),
            'Levelized Cost Per kWh Consumed': levelized_cost,
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


def format_column_name(x):
    x = x.replace('_', ' ')
    # Encourage spreadsheet programs to include empty columns when sorting rows
    return x or '-'


def format_technology(x):
    x = x.replace('_', ' ')
    return x.title()
