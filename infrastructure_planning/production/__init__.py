from invisibleroads_macros.math import divide_safely
from math import ceil

from ..exceptions import ExpectedPositive
from ..macros import interpolate_values


def adjust_for_losses(x, *fractional_losses):
    y = x
    for fractional_loss in fractional_losses:
        y = divide_safely(y, 1 - fractional_loss, 0)
    return y


def prepare_system_cost(
        option_table, capacity_column, desired_system_capacity):
    t = option_table.copy()
    t['raw_cost_per_unit_capacity'] = t['raw_cost'] / t[capacity_column]
    x = interpolate_values(t, capacity_column, desired_system_capacity)
    # Extrapolate
    raw_cost = desired_system_capacity * x['raw_cost_per_unit_capacity']
    installation_cost = raw_cost * x[
        'installation_cost_as_percent_of_raw_cost'] / float(100)
    return {
        'actual_system_' + capacity_column: int(ceil(desired_system_capacity)),
        'raw_cost': raw_cost,
        'installation_cost': installation_cost,
        'maintenance_cost_per_year': raw_cost * x[
            'maintenance_cost_per_year_as_percent_of_raw_cost'] / float(100),
        'replacement_cost_per_year': divide_safely(
            raw_cost + installation_cost, x['lifetime_in_years'],
            ExpectedPositive('lifetime_in_years')),
    }
