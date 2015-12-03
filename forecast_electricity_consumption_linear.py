from argparse import ArgumentParser
from crosscompute_table import TableType
from invisibleroads_macros.disk import make_enumerated_folder_for, make_folder
from invisibleroads_macros.log import format_summary

from infrastructure_planning.electricity.consumption.linear import (
    forecast_electricity_consumption)


if __name__ == '__main__':
    argument_parser = ArgumentParser()
    argument_parser.add_argument(
        '--target_folder', metavar='FOLDER', type=make_folder)
    argument_parser.add_argument(
        '--demographic_table_path', metavar='PATH', required=True)
    argument_parser.add_argument(
        '--name_column', metavar='COLUMN', required=True)
    argument_parser.add_argument(
        '--population_column', metavar='COLUMN', required=True)
    argument_parser.add_argument(
        '--year_column', metavar='COLUMN', required=True)
    argument_parser.add_argument(
        '--target_year', metavar='YEAR', type=int, required=True)
    argument_parser.add_argument(
        '--yearly_population_growth_percent', metavar='PERCENT', type=float,
        required=True)
    argument_parser.add_argument(
        '--electricity_consumption_per_capita_table_path', metavar='PATH',
        required=True)
    args = argument_parser.parse_args()
    d = forecast_electricity_consumption(
        args.target_folder or make_enumerated_folder_for(__file__),
        TableType().load(args.demographic_table_path),
        args.name_column,
        args.population_column,
        args.year_column,
        args.target_year,
        args.yearly_population_growth_percent,
        TableType().load(args.electricity_consumption_per_capita_table_path))
    print(format_summary(d))
