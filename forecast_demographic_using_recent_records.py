from argparse import ArgumentParser
from infrastructure_planning.demography.linear import (
    forecast_demographic_using_recent_records)
from infrastructure_planning.exceptions import InvalidData
from invisibleroads_macros.disk import make_enumerated_folder_for, make_folder
from invisibleroads_macros.log import format_summary
from os.path import join
from pandas import read_csv


def run(
        target_folder,
        target_year,
        demographic_by_year_table,
        demographic_by_year_table_name_column,
        demographic_by_year_table_year_column,
        demographic_by_year_table_population_column,
        default_yearly_population_growth_percent):
    d = []
    try:
        demographic_by_year_table = forecast_demographic_using_recent_records(
            target_year,
            demographic_by_year_table,
            demographic_by_year_table_name_column,
            demographic_by_year_table_year_column,
            demographic_by_year_table_population_column,
            default_yearly_population_growth_percent)
    except InvalidData as e:
        exit('demographic_by_year_table.error = %s' % e)
    demographic_by_year_table_path = join(
        target_folder, 'demographic-by-year.csv')
    demographic_by_year_table.to_csv(
        demographic_by_year_table_path, index=False)
    d.append((
        'demographic_by_year_table_path',
        demographic_by_year_table_path))

    columns = demographic_by_year_table.columns
    if 'Latitude' in columns and 'Longitude' in columns:
        demographic_by_year_geotable_path = join(
            target_folder, 'demographic-by-year.msg')
        demographic_by_year_geotable = demographic_by_year_table.fillna(
            method='ffill').groupby(
            demographic_by_year_table_name_column).last()
        # Set radius
        demographic_by_year_geotable['RadiusInPixelsRange10-50FromSum'] = \
            demographic_by_year_geotable[
                demographic_by_year_table_population_column]
        # Set fill color
        forecast_populations = demographic_by_year_table.groupby(
            demographic_by_year_table_name_column).last()[
                demographic_by_year_table_population_column]
        original_populations = demographic_by_year_table.groupby(
            demographic_by_year_table_name_column).first()[
                demographic_by_year_table_population_column]
        demographic_by_year_geotable['FillColor'] = (
            forecast_populations - original_populations).apply(
                lambda x: 'r' if x > 0 else 'b')
        # Save table
        demographic_by_year_geotable.to_msgpack(
            demographic_by_year_geotable_path, compress='blosc')
        d.insert(0, (
            'demographic_by_year_geotable_path',
            demographic_by_year_geotable_path))
    return d


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

        read_csv(args.demographic_by_year_table_path),
        args.demographic_by_year_table_name_column,
        args.demographic_by_year_table_year_column,
        args.demographic_by_year_table_population_column,
        args.default_yearly_population_growth_percent)
    print(format_summary(d))
