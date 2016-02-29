import numpy as np
from invisibleroads_macros.date import parse_date_safely
from scipy.optimize import fsolve


def compute_levelized_cost(time_production_cost_packs, discount_rate_percent):
    time_production_cost_array = np.array(time_production_cost_packs)
    time_production_packs = time_production_cost_array[:, [0, 1]]
    time_cost_packs = time_production_cost_array[:, [0, 2]]

    discounted_cost = compute_discounted_cash_flow(
        time_cost_packs, discount_rate_percent)
    discounted_production = compute_discounted_cash_flow(
        time_production_packs, discount_rate_percent)

    return discounted_cost / discounted_production


def compute_discounted_cash_flow(time_value_packs, discount_rate_percent):
    time_value_packs = sort_time_packs(time_value_packs)
    discount_rate_factor = 1 + discount_rate_percent / 100.
    values = [value for time, value in time_value_packs]
    return sum(x / discount_rate_factor ** t for t, x in enumerate(values))


def compute_break_even_time(time_value_packs, discount_rate_percent):
    time_value_packs = sort_time_packs(time_value_packs)
    for end_index in xrange(1, len(time_value_packs) + 1):
        discounted_cash_flow = compute_discounted_cash_flow(
            time_value_packs[:end_index], discount_rate_percent)
        if discounted_cash_flow >= 0:
            break_even_time = time_value_packs[end_index - 1][0]
            break
    else:
        break_even_time = None
    return break_even_time


def compute_internal_return_rate(time_value_packs):

    def f(discount_rate_percent):
        return compute_discounted_cash_flow(
            time_value_packs, discount_rate_percent)

    return fsolve(f, 0)[0]


def sort_time_packs(time_packs):
    return sorted(time_packs, key=lambda x: parse_date_safely(str(x[0])))
