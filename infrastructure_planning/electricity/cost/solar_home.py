import numpy as np
from collections import OrderedDict
from pandas import Series

from ...production import adjust_for_losses, prepare_actual_system_capacity
from . import prepare_component_cost_by_year, prepare_internal_cost


def estimate_internal_cost(**keywords):
    return prepare_internal_cost([
        estimate_electricity_production_cost,
        estimate_electricity_internal_distribution_cost,
    ], keywords)


def estimate_external_cost():
    return [('external_discounted_cost', 0)]


def estimate_electricity_production_cost(**keywords):
    d = prepare_component_cost_by_year([
        ('panel', estimate_panel_cost),
        ('battery', estimate_battery_cost),
        ('balance', estimate_balance_cost),
    ], keywords, prefix='solar_home_')
    solar_home_system_loss_as_percent_of_total_production = keywords[
        'solar_home_system_loss_as_percent_of_total_production']
    d['electricity_production_in_kwh_by_year'] = adjust_for_losses(
        keywords['consumption_in_kwh_by_year'],
        solar_home_system_loss_as_percent_of_total_production / 100.)
    d['electricity_production_cost_by_year'] = d.pop('cost_by_year')
    return d


def estimate_electricity_internal_distribution_cost(**keywords):
    d = OrderedDict()
    years = keywords['population_by_year'].index
    d['electricity_internal_distribution_cost_by_year'] = Series(
        np.zeros(len(years)), index=years)
    return d


def estimate_panel_cost(
        maximum_consumption_in_kwh_per_year,
        peak_hours_of_sun_per_year,
        solar_home_system_loss_as_percent_of_total_production,
        solar_home_panel_table):
    # Estimate desired capacity
    maximum_production_in_kwh_per_year = adjust_for_losses(
        maximum_consumption_in_kwh_per_year,
        solar_home_system_loss_as_percent_of_total_production / 100.)
    desired_system_capacity_in_kw = maximum_production_in_kwh_per_year / float(
        peak_hours_of_sun_per_year)
    # Choose panel type
    return prepare_actual_system_capacity(
        desired_system_capacity_in_kw,
        solar_home_panel_table, 'capacity_in_kw')


def estimate_battery_cost(
        solar_home_panel_actual_system_capacity_in_kw,
        solar_home_battery_kwh_per_panel_kw,
        solar_home_battery_installation_lm_cost_per_battery_kwh,
        solar_home_battery_maintenance_lm_cost_per_kwh_per_year,
        solar_home_battery_lifetime_in_years):
    battery_storage_in_kwh = solar_home_panel_actual_system_capacity_in_kw * \
        solar_home_battery_kwh_per_panel_kw
    installation_lm_cost = battery_storage_in_kwh * \
        solar_home_battery_installation_lm_cost_per_battery_kwh
    d = OrderedDict()
    d['installation_lm_cost'] = installation_lm_cost
    d['maintenance_lm_cost_per_year'] = battery_storage_in_kwh * \
        solar_home_battery_maintenance_lm_cost_per_kwh_per_year
    d['replacement_lm_cost_per_year'] = installation_lm_cost / float(
        solar_home_battery_lifetime_in_years)
    return d


def estimate_balance_cost(
        solar_home_panel_actual_system_capacity_in_kw,
        solar_home_balance_installation_lm_cost_per_panel_kw,
        solar_home_balance_maintenance_lm_cost_per_panel_kw_per_year,
        solar_home_balance_lifetime_in_years):
    installation_lm_cost = solar_home_panel_actual_system_capacity_in_kw * \
        solar_home_balance_installation_lm_cost_per_panel_kw
    d = OrderedDict()
    d['installation_lm_cost'] = installation_lm_cost
    d['maintenance_lm_cost_per_year'] = \
        solar_home_panel_actual_system_capacity_in_kw * \
        solar_home_balance_maintenance_lm_cost_per_panel_kw_per_year
    d['replacement_lm_cost_per_year'] = installation_lm_cost / float(
        solar_home_balance_lifetime_in_years)
    return d
