from infrastructure_planning.macros import BasicArgumentParser, load_and_run
from infrastructure_planning.preprocessors import (
    normalize_demand_point_table)

from infrastructure_planning.demography.exponential import estimate_population


def add_arguments_for_estimate_population(x):
    x.add('demand_point_table_path')
    x.add('population_year')
    x.add('population_growth_as_percent_of_population_per_year')
    x.add('financing_year')
    x.add('time_horizon_in_years')


if __name__ == '__main__':
    x = BasicArgumentParser()
    add_arguments_for_estimate_population(x)
    load_and_run([
        normalize_demand_point_table,
    ], [
        estimate_population,
    ], x)
