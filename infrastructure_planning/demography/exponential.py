from pandas import Series

from ..exceptions import ValidationError


def estimate_population(
        population,
        population_year,
        population_growth_as_percent_of_population_per_year,
        financing_year,
        time_horizon_in_years):
    if financing_year < population_year:
        raise ValidationError(
            'financing_year', 'cannot be less than population_year')
    # Compute the population at financing_year
    base_population = _grow_exponentially(
        population, population_growth_as_percent_of_population_per_year,
        financing_year - population_year)
    # Compute the population over time_horizon_in_years
    year_increments = Series(range(time_horizon_in_years + 1))
    years = financing_year + year_increments
    populations = _grow_exponentially(
        base_population, population_growth_as_percent_of_population_per_year,
        year_increments)
    populations.index = years
    return {
        'population_by_year': populations,
    }


def _grow_exponentially(value, growth_as_percent, growth_count):
    return value * (1 + growth_as_percent / 100.) ** growth_count
