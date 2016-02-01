from argparse import ArgumentParser
from crosscompute_table import TableType
from invisibleroads_macros.disk import make_enumerated_folder_for, make_folder
from invisibleroads_macros.log import format_summary
from os.path import join

from infrastructure_planning.electricity.consumption.linear import (
    estimate_electricity_consumption_from_series)
from infrastructure_planning.exceptions import EmptyDataset


def run(target_folder, *args):
    try:
        electricity_consumption_by_year_table = \
            estimate_electricity_consumption_from_series(*args)
    except EmptyDataset as e:
        exit('electricity_consumption_per_capita_by_year_table.error = %s' % e)
    electricity_consumption_by_year_table_path = join(
        target_folder, 'electricity-consumption-by-year.csv')
    electricity_consumption_by_year_table.to_csv(
        electricity_consumption_by_year_table_path, index=False)
    return [(
        'electricity_consumption_by_year_table_path',
        electricity_consumption_by_year_table_path,
    )]


if __name__ == '__main__':
    argument_parser = ArgumentParser()
    argument_parser.add_argument(
        '--target_folder',
        metavar='FOLDER', type=make_folder)

    argument_parser.add_argument(
        '--demographic_by_year_table_path',
        metavar='PATH', required=True)
    argument_parser.add_argument(
        '--demographic_by_year_table_name_column',
        metavar='COLUMN', required=True)
    argument_parser.add_argument(
        '--demographic_by_year_table_year_column',
        metavar='COLUMN', required=True)
    argument_parser.add_argument(
        '--demographic_by_year_table_population_column',
        metavar='COLUMN', required=True)

    argument_parser.add_argument(
        '--electricity_consumption_per_capita_by_year_table_path',
        metavar='PATH', required=True)
    argument_parser.add_argument(
        '--electricity_consumption_per_capita_by_year_table_year_column',
        metavar='COLUMN', required=True)
    argument_parser.add_argument(
        '--electricity_consumption_per_capita_by_year_table_consumption_per_capita_column',  # noqa
        metavar='COLUMN', required=True)
    argument_parser.add_argument(
        '--default_yearly_electricity_consumption_growth_percent',
        metavar='PERCENT', type=float, required=True)

    args = argument_parser.parse_args()
    d = run(
        args.target_folder or make_enumerated_folder_for(__file__),

        TableType.load(
            args.demographic_by_year_table_path),
        args.demographic_by_year_table_name_column,
        args.demographic_by_year_table_year_column,
        args.demographic_by_year_table_population_column,

        TableType.load(
            args.electricity_consumption_per_capita_by_year_table_path),
        args.electricity_consumption_per_capita_by_year_table_year_column,
        args.electricity_consumption_per_capita_by_year_table_consumption_per_capita_column,  # noqa
        args.default_yearly_electricity_consumption_growth_percent)
    print(format_summary(d))
