from invisibleroads_macros.math import divide_safely

from ...exceptions import ExpectedPositive
from ...production import adjust_for_losses, prepare_system_cost


def estimate_panel_cost(
        final_consumption_in_kwh_per_year,
        peak_hours_of_sun_per_year,
        system_loss_as_percent_of_total_production,
        panel_table):
    final_production_in_kwh_per_year = adjust_for_losses(
        final_consumption_in_kwh_per_year,
        system_loss_as_percent_of_total_production / 100.)
    desired_system_capacity_in_kw = divide_safely(
        final_production_in_kwh_per_year, peak_hours_of_sun_per_year,
        float('inf'))
    return prepare_system_cost(
        panel_table, 'capacity_in_kw', desired_system_capacity_in_kw)


def estimate_battery_cost(
        panel_actual_system_capacity_in_kw,
        battery_kwh_per_panel_kw,
        battery_raw_cost_per_battery_kwh,
        battery_installation_cost_as_percent_of_raw_cost,
        battery_maintenance_cost_per_year_as_percent_of_raw_cost,
        battery_lifetime_in_years):
    battery_storage_in_kwh = panel_actual_system_capacity_in_kw * \
        battery_kwh_per_panel_kw
    raw_cost = battery_storage_in_kwh * \
        battery_raw_cost_per_battery_kwh
    installation_cost = raw_cost * \
        battery_installation_cost_as_percent_of_raw_cost
    maintenance_cost_per_year = raw_cost * \
        battery_maintenance_cost_per_year_as_percent_of_raw_cost
    replacement_cost_per_year = divide_safely(
        raw_cost + installation_cost, battery_lifetime_in_years,
        ExpectedPositive('battery_lifetime_in_years'))
    return {
        'raw_cost': raw_cost,
        'installation_cost': installation_cost,
        'maintenance_cost_per_year': maintenance_cost_per_year,
        'replacement_cost_per_year': replacement_cost_per_year,
    }


def estimate_balance_cost(
        panel_actual_system_capacity_in_kw,
        balance_raw_cost_per_panel_kw,
        balance_installation_cost_as_percent_of_raw_cost,
        balance_maintenance_cost_per_year_as_percent_of_raw_cost,
        balance_lifetime_in_years):
    raw_cost = panel_actual_system_capacity_in_kw * \
        balance_raw_cost_per_panel_kw
    installation_cost = raw_cost * \
        balance_installation_cost_as_percent_of_raw_cost
    maintenance_cost_per_year = raw_cost * \
        balance_maintenance_cost_per_year_as_percent_of_raw_cost
    replacement_cost_per_year = divide_safely(
        raw_cost + installation_cost, balance_lifetime_in_years,
        ExpectedPositive('balance_lifetime_in_years'))
    return {
        'raw_cost': raw_cost,
        'installation_cost': installation_cost,
        'maintenance_cost_per_year': maintenance_cost_per_year,
        'replacement_cost_per_year': replacement_cost_per_year,
    }
