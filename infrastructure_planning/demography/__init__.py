from ..macros import get_final_value


def estimate_population_profile(population_by_year):
    return {
        'final_population': get_final_value(population_by_year),
    }
