from infrastructure_planning.macros import (
    BasicArgumentParser, load_and_run,
    # save_total_graph,
    wash_total_folder)
from infrastructure_planning.preprocessors import (
    normalize_demand_point_table,
    normalize_connection_type_table,
    normalize_grid_mv_transformer_table,
    normalize_diesel_mini_grid_generator_table,
    normalize_solar_home_panel_table,
    normalize_solar_mini_grid_panel_table,
    normalize_grid_mv_line_geotable)

from infrastructure_planning.demography import estimate_population_profile
from infrastructure_planning.demography.exponential import estimate_population
from infrastructure_planning.electricity.analysis import (
    estimate_proposed_cost_per_connection,
    estimate_total_count_by_technology,
    estimate_total_discounted_cost_by_technology,
    estimate_total_levelized_cost_by_technology, pick_proposed_technology)
from infrastructure_planning.electricity.consumption import (
    estimate_consumption_profile)
from infrastructure_planning.electricity.consumption.linear import (
    estimate_consumption_from_connection_type)
from infrastructure_planning.electricity.cost import (
    estimate_cost_profile, estimate_external_cost_by_technology,
    estimate_internal_cost_by_technology)
from infrastructure_planning.electricity.cost.grid import (
    estimate_grid_mv_line_budget,
    estimate_grid_mv_line_discounted_cost_per_meter)
from infrastructure_planning.electricity.demand import estimate_peak_demand
from infrastructure_planning.electricity.network import (
    assemble_total_grid_mv_line_network, sequence_total_grid_mv_line_network)
from infrastructure_planning.electricity.report import (
    save_total_lines, save_total_map, save_total_points,
    save_total_report_by_location, save_total_summary_by_grid_mv_line,
    save_total_summary_by_location, save_total_summary_by_technology,
    FULL_KEYS)

from estimate_grid_mv_line_budget_in_meters import (
    add_arguments_for_estimate_population)


if __name__ == '__main__':
    x = BasicArgumentParser()
    add_arguments_for_estimate_population(x)

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
        estimate_population_profile,
        estimate_consumption_from_connection_type,
        estimate_consumption_profile,
        estimate_peak_demand,
        estimate_internal_cost_by_technology,
        estimate_grid_mv_line_discounted_cost_per_meter,
        estimate_grid_mv_line_budget,
        assemble_total_grid_mv_line_network,
        sequence_total_grid_mv_line_network,
        estimate_external_cost_by_technology,
        estimate_cost_profile,
        pick_proposed_technology,
        estimate_proposed_cost_per_connection,
        estimate_total_count_by_technology,
        estimate_total_discounted_cost_by_technology,
        estimate_total_levelized_cost_by_technology,
        save_total_points,
        save_total_lines,
        save_total_report_by_location,
        save_total_summary_by_technology,
        save_total_summary_by_location,
        save_total_summary_by_grid_mv_line,
        save_total_map,
        # save_total_graph,
        wash_total_folder,
    ], x.parse_args().__dict__, FULL_KEYS)
