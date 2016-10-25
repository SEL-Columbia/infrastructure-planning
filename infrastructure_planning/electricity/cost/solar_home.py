from ...production import adjust_for_losses
from .solar import (
    estimate_panel_cost, estimate_battery_cost, estimate_balance_cost)
from . import (
    prepare_component_cost_by_year, prepare_external_cost,
    prepare_internal_cost)


def estimate_internal_cost(**keywords):
    return prepare_internal_cost([
        estimate_electricity_production_cost,
    ], keywords)


def estimate_external_cost(**keywords):
    return prepare_external_cost([
    ], keywords)


def estimate_electricity_production_cost(**keywords):
    component_cost_by_year, d = prepare_component_cost_by_year([
        ('panel', estimate_solar_home_panel_cost),
        ('battery', estimate_solar_home_battery_cost),
        ('balance', estimate_solar_home_balance_cost),
    ], keywords, prefix='solar_home_')
    d['electricity_production_in_kwh_by_year'] = adjust_for_losses(
        keywords['consumption_in_kwh_by_year'],
        keywords['solar_home_system_loss_as_percent_of_total_production'])
    d['electricity_production_cost_by_year'] = component_cost_by_year
    return d


def estimate_solar_home_panel_cost(
        final_consumption_in_kwh_per_year,
        peak_hours_of_sun_per_year,
        solar_home_system_loss_as_percent_of_total_production,
        solar_home_panel_table):
    return estimate_panel_cost(
        final_consumption_in_kwh_per_year,
        peak_hours_of_sun_per_year,
        solar_home_system_loss_as_percent_of_total_production,
        solar_home_panel_table)


def estimate_solar_home_battery_cost(
        solar_home_panel_actual_system_capacity_in_kw,
        solar_home_battery_kwh_per_panel_kw,
        solar_home_battery_raw_cost_per_battery_kwh,
        solar_home_battery_installation_cost_as_percent_of_raw_cost,
        solar_home_battery_maintenance_cost_per_year_as_percent_of_raw_cost,
        solar_home_battery_lifetime_in_years):
    return estimate_battery_cost(
        solar_home_panel_actual_system_capacity_in_kw,
        solar_home_battery_kwh_per_panel_kw,
        solar_home_battery_raw_cost_per_battery_kwh,
        solar_home_battery_installation_cost_as_percent_of_raw_cost,
        solar_home_battery_maintenance_cost_per_year_as_percent_of_raw_cost,
        solar_home_battery_lifetime_in_years)


def estimate_solar_home_balance_cost(
        solar_home_panel_actual_system_capacity_in_kw,
        solar_home_balance_raw_cost_per_panel_kw,
        solar_home_balance_installation_cost_as_percent_of_raw_cost,
        solar_home_balance_maintenance_cost_per_year_as_percent_of_raw_cost,
        solar_home_balance_lifetime_in_years):
    return estimate_balance_cost(
        solar_home_panel_actual_system_capacity_in_kw,
        solar_home_balance_raw_cost_per_panel_kw,
        solar_home_balance_installation_cost_as_percent_of_raw_cost,
        solar_home_balance_maintenance_cost_per_year_as_percent_of_raw_cost,
        solar_home_balance_lifetime_in_years)
