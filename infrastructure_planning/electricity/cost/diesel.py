from invisibleroads_macros.math import divide_safely
from pandas import DataFrame, Series

from ...production import adjust_for_losses, prepare_system_cost


def estimate_generator_cost(
        peak_demand_in_kw, system_loss_as_percent_of_total_production,
        generator_table):
    desired_system_capacity_in_kw = adjust_for_losses(
        peak_demand_in_kw, system_loss_as_percent_of_total_production)
    return prepare_system_cost(
        generator_table, 'capacity_in_kw', desired_system_capacity_in_kw)


def estimate_fuel_cost(
        consumption_in_kwh_by_year,
        system_loss_as_percent_of_total_production,
        generator_actual_system_capacity_in_kw,
        generator_minimum_hours_of_production_per_year,
        generator_fuel_liters_consumed_per_kwh,
        fuel_cost_per_liter):
    production_in_kwh_by_year = adjust_for_losses(
        consumption_in_kwh_by_year, system_loss_as_percent_of_total_production)
    desired_hours_of_production_by_year = divide_safely(
        production_in_kwh_by_year,
        generator_actual_system_capacity_in_kw, float('inf'))
    years = production_in_kwh_by_year.index
    minimum_hours_of_production_by_year = Series([
        generator_minimum_hours_of_production_per_year,
    ] * len(years), index=years)
    effective_hours_of_production_by_year = DataFrame({
        'desired': desired_hours_of_production_by_year,
        'minimum': minimum_hours_of_production_by_year,
    }).max(axis=1)
    return {
        'effective_hours_of_production_by_year':
            effective_hours_of_production_by_year,
        'fuel_cost_by_year': fuel_cost_per_liter *
            generator_fuel_liters_consumed_per_kwh *
            generator_actual_system_capacity_in_kw *
            effective_hours_of_production_by_year,
        'electricity_production_in_kwh_by_year': production_in_kwh_by_year,
    }
