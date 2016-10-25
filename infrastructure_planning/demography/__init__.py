import numpy as np
from pandas import Series

from ..macros import get_final_value


def estimate_population_profile(population_by_year):
    years = population_by_year.index
    zero_by_year = Series(np.zeros(len(years)), index=years)
    return {
        'final_population': get_final_value(population_by_year),
        'zero_by_year': zero_by_year,
    }
