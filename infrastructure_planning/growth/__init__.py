import numpy as np

from ..exceptions import InvalidData


def get_default_slope(growth_percent, year_packs):
    if hasattr(year_packs, 'tolist'):
        year_packs = year_packs.tolist()
    return sorted(year_packs)[-1][1] * growth_percent / 100.


def get_future_years(target_year, year_packs):
    past_years = sorted(x[0] for x in year_packs)
    future_years = range(int(past_years[-1]) + 1, target_year)
    if target_year not in past_years:
        future_years.append(target_year)
    return future_years


def split_xys(xys, default_slope=0):
    try:
        xs, ys = zip(*xys)
    except ValueError:
        raise InvalidData('must have at least one row')
    if len(set(xs)) == 1:
        xs = list(xs) + [xs[0] + 1]
        ys = list(ys) + [np.mean(ys) + default_slope]
    return xs, ys
