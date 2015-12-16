from argparse import ArgumentParser
from crosscompute_table import TableType
from infrastructure_planning.demography.linear import (
    forecast_demographic_from_series)
from invisibleroads_macros.disk import make_enumerated_folder_for, make_folder
from invisibleroads_macros.log import format_summary
from os.path import join


def run(target_folder, *args):
    demographic_by_year_table = forecast_demographic_from_series(*args)
    demographic_by_year_table_path = join(
        target_folder, 'demographic-by-year.csv')
    demographic_by_year_table.to_csv(
        demographic_by_year_table_path, index=False)
    return [(
        'demographic_by_year_table_path',
        demographic_by_year_table_path
    )]


if __name__ == '__main__':
    argument_parser = ArgumentParser()
    argument_parser.add_argument(
        '--target_folder',
        metavar='FOLDER', type=make_folder)
    argument_parser.add_argument(
        '--target_year',
        metavar='YEAR', type=int, required=True)

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
        '--default_yearly_population_growth_percent',
        metavar='PERCENT', type=float, required=True)

    args = argument_parser.parse_args()
    d = run(
        args.target_folder or make_enumerated_folder_for(__file__),
        args.target_year,

        TableType().load(
            args.demographic_by_year_table_path),
        args.demographic_by_year_table_name_column,
        args.demographic_by_year_table_year_column,
        args.demographic_by_year_table_population_column,
        args.default_yearly_population_growth_percent)
    print(format_summary(d))
