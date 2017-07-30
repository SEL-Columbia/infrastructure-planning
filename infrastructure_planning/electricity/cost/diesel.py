from invisibleroads_macros.calculator import divide_safely
from pandas import DataFrame, Series

from ...macros import get_final_value
from ...production import adjust_for_losses, prepare_system_capacity_cost


def estimate_generator_cost(
        peak_demand_in_kw, system_loss_as_percent_of_total_production,
        generator_table):
    desired_system_capacity_in_kw = adjust_for_losses(
        peak_demand_in_kw, system_loss_as_percent_of_total_production)
    return prepare_system_capacity_cost(
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
    hours_of_production_by_year = DataFrame({
        'desired': desired_hours_of_production_by_year,
        'minimum': minimum_hours_of_production_by_year,
    }).max(axis=1)
    fuel_cost_by_year = fuel_cost_per_liter * \
        generator_fuel_liters_consumed_per_kwh * \
        generator_actual_system_capacity_in_kw * \
        hours_of_production_by_year
    d = {}
    # Add yearly values
    d['hours_of_production_by_year'] = hours_of_production_by_year
    d['fuel_cost_by_year'] = fuel_cost_by_year
    d['electricity_production_in_kwh_by_year'] = production_in_kwh_by_year
    # Add final values
    d['final_hours_of_production_per_year'] = get_final_value(
        hours_of_production_by_year)
    d['final_fuel_cost_per_year'] = get_final_value(fuel_cost_by_year)
    d['final_electricity_production_in_kwh_per_year'] = get_final_value(
        production_in_kwh_by_year)
    return d
