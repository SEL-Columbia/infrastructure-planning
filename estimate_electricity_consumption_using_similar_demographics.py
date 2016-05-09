from argparse import ArgumentParser
from infrastructure_planning.growth.fitted import get_fitted_linear_function
from invisibleroads_macros.disk import make_enumerated_folder_for, make_folder
from invisibleroads_macros.log import format_summary
from os.path import join
from pandas import read_csv


def run(target_folder, *args):
    electricity_consumption_by_year_table = \
        estimate_consumption_using_similar_demographics(*args)
    electricity_consumption_by_year_table_path = join(
        target_folder, 'electricity-consumption-by-year.csv')
    electricity_consumption_by_year_table.to_csv(
        electricity_consumption_by_year_table_path, index=False)
    return [(
        'electricity_consumption_by_year_table_path',
        electricity_consumption_by_year_table_path,
    )]


def estimate_consumption_using_similar_demographics(
        demographic_by_year_table,
        demographic_by_year_table_population_column,
        consumption_by_population_table,
        consumption_by_population_table_population_column,
        consumption_by_population_table_consumption_column):
    population_consumption_packs = consumption_by_population_table[[
        consumption_by_population_table_population_column,
        consumption_by_population_table_consumption_column]].values
    estimate_consumption = get_fitted_linear_function(
        population_consumption_packs)
    consumption_by_year_table = demographic_by_year_table.copy()
    consumption_by_year_table[
        consumption_by_population_table_consumption_column
    ] = demographic_by_year_table[
        demographic_by_year_table_population_column
    ].apply(estimate_consumption)
    return consumption_by_year_table


if __name__ == '__main__':
    argument_parser = ArgumentParser()
    argument_parser.add_argument(
        '--target_folder',
        metavar='FOLDER', type=make_folder)

    argument_parser.add_argument(
        '--demographic_by_year_table_path',
        metavar='PATH', required=True)
    argument_parser.add_argument(
        '--demographic_by_year_table_population_column',
        metavar='COLUMN', required=True)

    argument_parser.add_argument(
        '--electricity_consumption_by_population_table_path',
        metavar='PATH', required=True)
    argument_parser.add_argument(
        '--electricity_consumption_by_population_table_population_column',
        metavar='COLUMN', required=True)
    argument_parser.add_argument(
        '--electricity_consumption_by_population_table_consumption_column',
        metavar='COLUMN', required=True)

    args = argument_parser.parse_args()
    d = run(
        args.target_folder or make_enumerated_folder_for(__file__),

        read_csv(args.demographic_by_year_table_path),
        args.demographic_by_year_table_population_column,

        read_csv(args.electricity_consumption_by_population_table_path),
        args.electricity_consumption_by_population_table_population_column,
        args.electricity_consumption_by_population_table_consumption_column)
    print(format_summary(d))
