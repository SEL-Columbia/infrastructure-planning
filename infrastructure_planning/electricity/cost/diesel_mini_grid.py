from invisibleroads_macros.math import divide_safely
from pandas import DataFrame, Series

from ...macros import compute
from ...production import adjust_for_losses, prepare_actual_system_capacity
from .mini_grid import estimate_lv_line_cost, estimate_lv_connection_cost
from . import prepare_component_cost_by_year, prepare_internal_cost


def estimate_internal_cost(**keywords):
    return prepare_internal_cost([
        estimate_electricity_production_cost,
        estimate_electricity_internal_distribution_cost,
    ], keywords)


def estimate_external_cost():
    return {'external_discounted_cost': 0}


def estimate_electricity_production_cost(**keywords):
    d = prepare_component_cost_by_year([
        ('generator', estimate_diesel_mini_grid_generator_cost),
    ], keywords, prefix='diesel_mini_grid_')
    d.update(compute(estimate_diesel_mini_grid_fuel_cost, keywords, d))
    d['electricity_production_cost_by_year'] = d.pop('cost_by_year') + d[
        'diesel_mini_grid_fuel_cost_by_year']
    return d


def estimate_electricity_internal_distribution_cost(
        **keywords):
    d = prepare_component_cost_by_year([
        ('lv_line', estimate_diesel_mini_grid_lv_line_cost),
        ('lv_connection', estimate_diesel_mini_grid_lv_connection_cost),
    ], keywords, prefix='diesel_mini_grid_')
    d['electricity_internal_distribution_cost_by_year'] = d.pop('cost_by_year')
    return d


def estimate_diesel_mini_grid_generator_cost(
        peak_demand_in_kw,
        diesel_mini_grid_system_loss_as_percent_of_total_production,
        diesel_mini_grid_generator_table):
    # Estimate desired capacity
    desired_system_capacity_in_kw = adjust_for_losses(
        peak_demand_in_kw,
        diesel_mini_grid_system_loss_as_percent_of_total_production / 100.)
    # Choose generator type
    return prepare_actual_system_capacity(
        desired_system_capacity_in_kw,
        diesel_mini_grid_generator_table, 'capacity_in_kw')


def estimate_diesel_mini_grid_fuel_cost(
        consumption_in_kwh_by_year,
        diesel_mini_grid_system_loss_as_percent_of_total_production,
        diesel_mini_grid_generator_actual_system_capacity_in_kw,
        diesel_mini_grid_generator_minimum_hours_of_production_per_year,
        diesel_mini_grid_generator_fuel_liters_consumed_per_kwh,
        diesel_mini_grid_fuel_cost_per_liter):
    d = {}
    production_in_kwh_by_year = adjust_for_losses(
        consumption_in_kwh_by_year,
        diesel_mini_grid_system_loss_as_percent_of_total_production / 100.)
    desired_hours_of_production_by_year = divide_safely(
        production_in_kwh_by_year,
        diesel_mini_grid_generator_actual_system_capacity_in_kw, float('inf'))
    years = production_in_kwh_by_year.index
    minimum_hours_of_production_by_year = Series([
        diesel_mini_grid_generator_minimum_hours_of_production_per_year,
    ] * len(years), index=years)
    effective_hours_of_production_by_year = DataFrame({
        'desired': desired_hours_of_production_by_year,
        'minimum': minimum_hours_of_production_by_year,
    }).max(axis=1)
    d['diesel_mini_grid_effective_hours_of_production_by_year'] = \
        effective_hours_of_production_by_year
    d['diesel_mini_grid_fuel_cost_by_year'] = \
        diesel_mini_grid_fuel_cost_per_liter * \
        diesel_mini_grid_generator_fuel_liters_consumed_per_kwh * \
        diesel_mini_grid_generator_actual_system_capacity_in_kw * \
        effective_hours_of_production_by_year
    d['electricity_production_in_kwh_by_year'] = production_in_kwh_by_year
    return d


def estimate_diesel_mini_grid_lv_line_cost(
        final_connection_count,
        line_length_adjustment_factor,
        average_distance_between_buildings_in_meters,
        diesel_mini_grid_lv_line_installation_lm_cost_per_meter,
        diesel_mini_grid_lv_line_maintenance_lm_cost_per_meter_per_year,
        diesel_mini_grid_lv_line_lifetime_in_years):
    return estimate_lv_line_cost(
        final_connection_count,
        line_length_adjustment_factor,
        average_distance_between_buildings_in_meters,
        diesel_mini_grid_lv_line_installation_lm_cost_per_meter,
        diesel_mini_grid_lv_line_maintenance_lm_cost_per_meter_per_year,
        diesel_mini_grid_lv_line_lifetime_in_years)


def estimate_diesel_mini_grid_lv_connection_cost(
        final_connection_count,
        diesel_mini_grid_lv_connection_installation_lm_cost_per_connection,
        diesel_mini_grid_lv_connection_maintenance_lm_cost_per_connection_per_year,  # noqa
        diesel_mini_grid_lv_connection_lifetime_in_years):
    return estimate_lv_connection_cost(
        final_connection_count,
        diesel_mini_grid_lv_connection_installation_lm_cost_per_connection,
        diesel_mini_grid_lv_connection_maintenance_lm_cost_per_connection_per_year,  # noqa
        diesel_mini_grid_lv_connection_lifetime_in_years)
