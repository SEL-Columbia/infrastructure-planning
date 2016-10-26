from ...macros import compute
from .diesel import estimate_fuel_cost, estimate_generator_cost
from .mini_grid import estimate_lv_line_cost, estimate_lv_connection_cost
from . import (
    prepare_component_cost_by_year, prepare_external_cost,
    prepare_internal_cost)


def estimate_internal_cost(**keywords):
    return prepare_internal_cost([
        estimate_system_capacity_cost,
        estimate_electricity_production_cost,
        estimate_internal_distribution_cost,
    ], keywords)


def estimate_external_cost(**keywords):
    return prepare_external_cost([
    ], keywords)


def estimate_system_capacity_cost(**keywords):
    component_cost_by_year, d = prepare_component_cost_by_year([
        ('generator', estimate_diesel_mini_grid_generator_cost),
    ], keywords, prefix='diesel_mini_grid_')
    d['system_capacity_cost_by_year'] = component_cost_by_year
    return d


def estimate_electricity_production_cost(**keywords):
    functions = [
        estimate_diesel_mini_grid_fuel_cost,
    ]
    d = {}
    for f in functions:
        d.update(compute(f, keywords, d))
    d['electricity_production_cost_by_year'] = d['fuel_cost_by_year']
    return d


def estimate_internal_distribution_cost(
        **keywords):
    component_cost_by_year, d = prepare_component_cost_by_year([
        ('lv_line', estimate_diesel_mini_grid_lv_line_cost),
        ('lv_connection', estimate_diesel_mini_grid_lv_connection_cost),
    ], keywords, prefix='diesel_mini_grid_')
    d['internal_distribution_cost_by_year'] = component_cost_by_year
    return d


def estimate_diesel_mini_grid_generator_cost(
        peak_demand_in_kw,
        diesel_mini_grid_system_loss_as_percent_of_total_production,
        diesel_mini_grid_generator_table):
    return estimate_generator_cost(
        peak_demand_in_kw,
        diesel_mini_grid_system_loss_as_percent_of_total_production,
        diesel_mini_grid_generator_table)


def estimate_diesel_mini_grid_fuel_cost(
        consumption_in_kwh_by_year,
        diesel_mini_grid_system_loss_as_percent_of_total_production,
        diesel_mini_grid_generator_actual_system_capacity_in_kw,
        diesel_mini_grid_generator_minimum_hours_of_production_per_year,
        diesel_mini_grid_generator_fuel_liters_consumed_per_kwh,
        diesel_mini_grid_fuel_cost_per_liter):
    return estimate_fuel_cost(
        consumption_in_kwh_by_year,
        diesel_mini_grid_system_loss_as_percent_of_total_production,
        diesel_mini_grid_generator_actual_system_capacity_in_kw,
        diesel_mini_grid_generator_minimum_hours_of_production_per_year,
        diesel_mini_grid_generator_fuel_liters_consumed_per_kwh,
        diesel_mini_grid_fuel_cost_per_liter)


def estimate_diesel_mini_grid_lv_line_cost(
        final_connection_count,
        line_length_adjustment_factor,
        average_distance_between_buildings_in_meters,
        diesel_mini_grid_lv_line_raw_cost_per_meter,
        diesel_mini_grid_lv_line_installation_cost_as_percent_of_raw_cost,
        diesel_mini_grid_lv_line_maintenance_cost_per_year_as_percent_of_raw_cost,  # noqa
        diesel_mini_grid_lv_line_lifetime_in_years):
    return estimate_lv_line_cost(
        final_connection_count,
        line_length_adjustment_factor,
        average_distance_between_buildings_in_meters,
        diesel_mini_grid_lv_line_raw_cost_per_meter,
        diesel_mini_grid_lv_line_installation_cost_as_percent_of_raw_cost,
        diesel_mini_grid_lv_line_maintenance_cost_per_year_as_percent_of_raw_cost,  # noqa
        diesel_mini_grid_lv_line_lifetime_in_years)


def estimate_diesel_mini_grid_lv_connection_cost(
        final_connection_count,
        diesel_mini_grid_lv_connection_raw_cost,
        diesel_mini_grid_lv_connection_installation_cost_as_percent_of_raw_cost,  # noqa
        diesel_mini_grid_lv_connection_maintenance_cost_per_year_as_percent_of_raw_cost,  # noqa
        diesel_mini_grid_lv_connection_lifetime_in_years):
    return estimate_lv_connection_cost(
        final_connection_count,
        diesel_mini_grid_lv_connection_raw_cost,
        diesel_mini_grid_lv_connection_installation_cost_as_percent_of_raw_cost,  # noqa
        diesel_mini_grid_lv_connection_maintenance_cost_per_year_as_percent_of_raw_cost,  # noqa
        diesel_mini_grid_lv_connection_lifetime_in_years)
