from .solar import (
    estimate_panel_cost, estimate_battery_cost, estimate_balance_cost)
from .mini_grid import estimate_lv_line_cost, estimate_lv_connection_cost
from . import (
    prepare_component_cost_by_year, prepare_external_cost,
    prepare_internal_cost)


def estimate_internal_cost(**keywords):
    return prepare_internal_cost([
        estimate_system_capacity_cost,
        estimate_internal_distribution_cost,
    ], keywords)


def estimate_external_cost(**keywords):
    return prepare_external_cost([
    ], keywords)


def estimate_system_capacity_cost(**keywords):
    component_cost_by_year, d = prepare_component_cost_by_year([
        ('panel', estimate_solar_mini_grid_panel_cost),
        ('battery', estimate_solar_mini_grid_battery_cost),
        ('balance', estimate_solar_mini_grid_balance_cost),
    ], keywords, prefix='solar_mini_grid_')
    d['system_capacity_cost_by_year'] = component_cost_by_year
    return d


def estimate_internal_distribution_cost(**keywords):
    component_cost_by_year, d = prepare_component_cost_by_year([
        ('lv_line', estimate_solar_mini_grid_lv_line_cost),
        ('lv_connection', estimate_solar_mini_grid_lv_connection_cost),
    ], keywords, prefix='solar_mini_grid_')
    d['internal_distribution_cost_by_year'] = component_cost_by_year
    return d


def estimate_solar_mini_grid_panel_cost(
        final_consumption_in_kwh_per_year,
        peak_hours_of_sun_per_year,
        solar_mini_grid_system_loss_as_percent_of_total_production,
        solar_mini_grid_panel_table):
    return estimate_panel_cost(
        final_consumption_in_kwh_per_year,
        peak_hours_of_sun_per_year,
        solar_mini_grid_system_loss_as_percent_of_total_production,
        solar_mini_grid_panel_table)


def estimate_solar_mini_grid_battery_cost(
        solar_mini_grid_panel_actual_system_capacity_in_kw,
        solar_mini_grid_battery_kwh_per_panel_kw,
        solar_mini_grid_battery_raw_cost_per_battery_kwh,
        solar_mini_grid_battery_installation_cost_as_percent_of_raw_cost,
        solar_mini_grid_battery_maintenance_cost_per_year_as_percent_of_raw_cost,  # noqa
        solar_mini_grid_battery_lifetime_in_years):
    return estimate_battery_cost(
        solar_mini_grid_panel_actual_system_capacity_in_kw,
        solar_mini_grid_battery_kwh_per_panel_kw,
        solar_mini_grid_battery_raw_cost_per_battery_kwh,
        solar_mini_grid_battery_installation_cost_as_percent_of_raw_cost,
        solar_mini_grid_battery_maintenance_cost_per_year_as_percent_of_raw_cost,  # noqa
        solar_mini_grid_battery_lifetime_in_years)


def estimate_solar_mini_grid_balance_cost(
        solar_mini_grid_panel_actual_system_capacity_in_kw,
        solar_mini_grid_balance_raw_cost_per_panel_kw,
        solar_mini_grid_balance_installation_cost_as_percent_of_raw_cost,
        solar_mini_grid_balance_maintenance_cost_per_year_as_percent_of_raw_cost,  # noqa
        solar_mini_grid_balance_lifetime_in_years):
    return estimate_balance_cost(
        solar_mini_grid_panel_actual_system_capacity_in_kw,
        solar_mini_grid_balance_raw_cost_per_panel_kw,
        solar_mini_grid_balance_installation_cost_as_percent_of_raw_cost,
        solar_mini_grid_balance_maintenance_cost_per_year_as_percent_of_raw_cost,  # noqa
        solar_mini_grid_balance_lifetime_in_years)


def estimate_solar_mini_grid_lv_line_cost(
        final_connection_count,
        line_length_adjustment_factor,
        average_distance_between_buildings_in_meters,
        solar_mini_grid_lv_line_raw_cost_per_meter,
        solar_mini_grid_lv_line_installation_cost_as_percent_of_raw_cost,
        solar_mini_grid_lv_line_maintenance_cost_per_year_as_percent_of_raw_cost,  # noqa
        solar_mini_grid_lv_line_lifetime_in_years):
    return estimate_lv_line_cost(
        final_connection_count,
        line_length_adjustment_factor,
        average_distance_between_buildings_in_meters,
        solar_mini_grid_lv_line_raw_cost_per_meter,
        solar_mini_grid_lv_line_installation_cost_as_percent_of_raw_cost,
        solar_mini_grid_lv_line_maintenance_cost_per_year_as_percent_of_raw_cost,  # noqa
        solar_mini_grid_lv_line_lifetime_in_years)


def estimate_solar_mini_grid_lv_connection_cost(
        final_connection_count,
        solar_mini_grid_lv_connection_raw_cost,
        solar_mini_grid_lv_connection_installation_cost_as_percent_of_raw_cost,
        solar_mini_grid_lv_connection_maintenance_cost_per_year_as_percent_of_raw_cost,  # noqa
        solar_mini_grid_lv_connection_lifetime_in_years):
    return estimate_lv_connection_cost(
        final_connection_count,
        solar_mini_grid_lv_connection_raw_cost,
        solar_mini_grid_lv_connection_installation_cost_as_percent_of_raw_cost,
        solar_mini_grid_lv_connection_maintenance_cost_per_year_as_percent_of_raw_cost,  # noqa
        solar_mini_grid_lv_connection_lifetime_in_years)
