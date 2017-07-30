from invisibleroads_macros.calculator import divide_safely

from ..exceptions import ExpectedPositive
from ..macros import interpolate_values


def adjust_for_losses(x, *loss_percents):
    y = x
    for loss_percent in loss_percents:
        loss_fraction = loss_percent / 100.
        y = divide_safely(y, 1 - loss_fraction, 0)
    return y


def prepare_system_capacity_cost(
        option_table, capacity_column, desired_system_capacity):
    t = option_table.copy()
    t['raw_cost_per_unit_capacity'] = t['raw_cost'] / t[capacity_column]
    x = interpolate_values(t, capacity_column, desired_system_capacity)

    minimum_system_capacity = t[capacity_column].min()
    actual_system_capacity = max(
        desired_system_capacity, minimum_system_capacity)

    # Extrapolate
    raw_cost = actual_system_capacity * x['raw_cost_per_unit_capacity']
    installation_cost = raw_cost * x[
        'installation_cost_as_percent_of_raw_cost'] / 100.
    return {
        'actual_system_' + capacity_column: actual_system_capacity,
        'raw_cost': raw_cost,
        'installation_cost': installation_cost,
        'maintenance_cost_per_year': raw_cost * x[
            'maintenance_cost_per_year_as_percent_of_raw_cost'] / 100.,
        'replacement_cost_per_year': divide_safely(
            raw_cost + installation_cost, x['lifetime_in_years'],
            ExpectedPositive('lifetime_in_years')),
    }
