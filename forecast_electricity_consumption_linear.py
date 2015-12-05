from argparse import ArgumentParser
from crosscompute_table import TableType
from invisibleroads_macros.disk import make_enumerated_folder_for, make_folder
from invisibleroads_macros.log import format_summary
from os.path import join

from infrastructure_planning.electricity.consumption.linear import (
    forecast_electricity_consumption_from_demographic)


def run(target_folder, *args):
    electricity_consumption_table = \
        forecast_electricity_consumption_from_demographic(*args)
    electricity_consumption_table_path = join(
        target_folder, 'electricity_consumption.csv')
    electricity_consumption_table.to_csv(
        electricity_consumption_table_path, index=False)
    return [(
        'electricity_consumption_table_path',
        electricity_consumption_table_path,
    )]


if __name__ == '__main__':
    argument_parser = ArgumentParser()
    argument_parser.add_argument(
        '--target_folder', metavar='FOLDER', type=make_folder)
    argument_parser.add_argument(
        '--target_year', metavar='YEAR', type=int, required=True)
    argument_parser.add_argument(
        '--demographic_table_path', metavar='PATH', required=True)
    argument_parser.add_argument(
        '--demographic_name_column', metavar='COLUMN', required=True)
    argument_parser.add_argument(
        '--demographic_population_column', metavar='COLUMN', required=True)
    argument_parser.add_argument(
        '--demographic_year_column', metavar='COLUMN', required=True)
    argument_parser.add_argument(
        '--default_yearly_population_growth_percent', metavar='PERCENT',
        type=float, required=True)
    argument_parser.add_argument(
        '--electricity_consumption_per_capita_table_path', metavar='PATH',
        required=True)
    argument_parser.add_argument(
        '--electricity_consumption_per_capita_year_column', metavar='COLUMN',
        required=True)
    argument_parser.add_argument(
        '--electricity_consumption_per_capita_consumption_per_capita_column',
        metavar='COLUMN', required=True)
    argument_parser.add_argument(
        '--default_yearly_electricity_consumption_growth_percent',
        metavar='PERCENT', type=float, required=True)
    args = argument_parser.parse_args()
    d = run(
        args.target_folder or make_enumerated_folder_for(__file__),
        args.target_year,
        TableType().load(args.demographic_table_path),
        args.demographic_name_column,
        args.demographic_population_column,
        args.demographic_year_column,
        args.default_yearly_population_growth_percent,
        TableType().load(args.electricity_consumption_per_capita_table_path),
        args.electricity_consumption_per_capita_year_column,
        args.electricity_consumption_per_capita_consumption_per_capita_column,
        args.default_yearly_electricity_consumption_growth_percent)
    print(format_summary(d))
