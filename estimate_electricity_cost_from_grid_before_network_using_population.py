from argparse import ArgumentParser
from collections import OrderedDict
from crosscompute_table import TableType
from invisibleroads_macros.disk import make_enumerated_folder_for, make_folder
from invisibleroads_macros.log import format_summary
from os.path import join


NAME_COLUMN = 'Name'


def run(
        target_folder,
        # Finance
        time_horizon_in_years,
        discount_rate_as_percent_per_year,
        # Demography
        demographic_table,
        population_growth_rate_as_percent_per_year,
        # Consumption
        connection_count_per_thousand_people,
        consumption_per_connection_in_kwh):
    d = OrderedDict()

    target_path = join(target_folder, 'demographic_table.csv')
    demographic_table.to_csv(target_path, index=False)
    d['demographic_table_path'] = target_path

    target_path = join(target_folder, 'demographic_geotable.csv')
    demographic_geotable = demographic_table.copy()
    demographic_geotable['RadiusInPixelsRange10-50FromSum'] = \
        demographic_geotable['Population']
    demographic_geotable['FillGreens'] = \
        demographic_geotable['Year']
    demographic_geotable.to_csv(target_path, index=False)
    d['demographic_streets_satellite_geotable_path'] = target_path

    """
    # for name, table in demographic_table.groupby(NAME_COLUMN):
        # pass

        # Get cost breakdown
        # Get discounted cost
        # Get levelized cost

    # Get aggregated cost breakdown
    # Get aggregated discounted cost
    # Get aggregated levelized cost
    """
    return d


if __name__ == '__main__':
    argument_parser = ArgumentParser()
    argument_parser.add_argument(
        '--target_folder',
        metavar='FOLDER', type=make_folder)

    argument_parser.add_argument(
        '--time_horizon_in_years',
        metavar='INTEGER', required=True, type=int)
    argument_parser.add_argument(
        '--discount_rate_as_percent_per_year',
        metavar='PERCENT', required=True, type=float)

    argument_parser.add_argument(
        '--demographic_table_path',
        metavar='PATH', required=True)
    argument_parser.add_argument(
        '--population_growth_rate_as_percent_per_year',
        metavar='INTEGER', required=True, type=int)

    argument_parser.add_argument(
        '--connection_count_per_thousand_people',
        metavar='INTEGER', required=True, type=float)
    argument_parser.add_argument(
        '--consumption_per_connection_in_kwh',
        metavar='INTEGER', required=True, type=float)

    args = argument_parser.parse_args()
    d = run(
        args.target_folder or make_enumerated_folder_for(__file__),

        args.time_horizon_in_years,
        args.discount_rate_as_percent_per_year,

        TableType.load(
            args.demographic_table_path),
        args.population_growth_rate_as_percent_per_year,

        args.connection_count_per_thousand_people,
        args.consumption_per_connection_in_kwh)
    print(format_summary(d))
