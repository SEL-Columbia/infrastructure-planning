from argparse import ArgumentParser
from crosscompute_table import TableType
from invisibleroads_macros.disk import make_enumerated_folder_for, make_folder
from invisibleroads_macros.log import format_summary


def run(
        target_folder,
        electricity_consumption_by_year_table_path,
        electricity_consumption_by_year_table_consumption_column):

    # For each location,

        # Get maximum_consumption_per_year
        maximum_consumption_per_year = 
        # Get peak_demand
        # Get desired system capacity in kilowatts
        # Load transformer table
        # Choose transformer type
        # Get selected_transformer_count
        # Get cost breakdown
        # Get discounted cost
        # Get levelized cost

    # Get aggregated cost breakdown
    # Get aggregated discounted cost
    # Get aggregated levelized cost

    return [(
    )]


if __name__ == '__main__':
    argument_parser = ArgumentParser()
    argument_parser.add_argument(
        '--target_folder',
        metavar='FOLDER', type=make_folder)

    argument_parser.add_argument(
        '--electricity_consumption_by_year_table_path',
        metavar='PATH', required=True)
    argument_parser.add_argument(
        '--electricity_consumption_by_year_table_consumption_column',
        metavar='COLUMN', required=True)

    args = argument_parser.parse_args()
    d = run(
        args.target_folder or make_enumerated_folder_for(__file__),

        TableType.load(
            args.electricity_consumption_by_year_table_path),
        args.electricity_consumption_by_year_table_name_column,
        args.electricity_consumption_by_year_table_consumption_column)
    print(format_summary(d))
