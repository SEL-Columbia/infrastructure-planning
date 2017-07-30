import numpy as np
from dateutil.parser import parse as parse_date
from scipy.optimize import fsolve


def compute_discounted_cash_flow(
        cash_flow_by_year, financing_year, discount_rate_as_percent):
    'Discount cash flow starting from the year of financing'
    year_increments = np.array(cash_flow_by_year.index - financing_year)
    year_increments[year_increments < 0] = 0  # Do not discount prior years
    discount_rate_as_factor = 1 + discount_rate_as_percent / 100.
    return sum(cash_flow_by_year / discount_rate_as_factor ** year_increments)


def compute_discounted_cash_flow_xxx(time_value_packs, discount_rate_percent):
    time_value_packs = sort_time_packs(time_value_packs)
    discount_rate_factor = 1 + discount_rate_percent / 100.
    values = [value for time, value in time_value_packs]
    return sum(x / discount_rate_factor ** t for t, x in enumerate(values))


def compute_break_even_time(time_value_packs, discount_rate_percent):
    time_value_packs = sort_time_packs(time_value_packs)
    for end_index in range(1, len(time_value_packs) + 1):
        discounted_cash_flow = compute_discounted_cash_flow_xxx(
            time_value_packs[:end_index], discount_rate_percent)
        if discounted_cash_flow >= 0:
            break_even_time = time_value_packs[end_index - 1][0]
            break
    else:
        break_even_time = None
    return break_even_time


def compute_internal_return_rate(time_value_packs):

    def f(discount_rate_percent):
        return compute_discounted_cash_flow_xxx(
            time_value_packs, discount_rate_percent)

    return fsolve(f, 0)[0]


def sort_time_packs(time_packs):
    return sorted(time_packs, key=lambda x: parse_date(str(x[0])))
