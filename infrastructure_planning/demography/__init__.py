from pandas import Series

from ..macros import get_final_value, make_zero_by_year


def estimate_population_profile(population_by_year):
    return {
        'final_population': get_final_value(population_by_year),
        'zero_by_year': make_zero_by_year(population_by_year),
    }
