from argparse import ArgumentParser
from infrastructure_planning.finance.valuation import compute_levelized_cost
from invisibleroads_macros.log import format_summary
from pandas import read_csv


def run(
        time_production_cost_table,
        time_column, production_column, cost_column,
        discount_rate_percent):

    levelized_cost = compute_levelized_cost(time_production_cost_table[[
        time_column,
        production_column,
        cost_column,
    ]].values, discount_rate_percent)

    return [
        ('levelized_cost', levelized_cost),
    ]


if __name__ == '__main__':
    argument_parser = ArgumentParser()

    argument_parser.add_argument(
        '--time_production_cost_table_path',
        metavar='PATH', required=True)
    argument_parser.add_argument(
        '--time_production_cost_table_time_column',
        metavar='COLUMN', required=True)
    argument_parser.add_argument(
        '--time_production_cost_table_production_column',
        metavar='COLUMN', required=True)
    argument_parser.add_argument(
        '--time_production_cost_table_cost_column',
        metavar='COLUMN', required=True)

    argument_parser.add_argument(
        '--discount_rate_percent',
        metavar='PERCENT', type=float, required=True)

    args = argument_parser.parse_args()
    d = run(
        read_csv(args.time_production_cost_table_path),
        args.time_production_cost_table_time_column,
        args.time_production_cost_table_production_column,
        args.time_production_cost_table_cost_column,
        args.discount_rate_percent)
    print(format_summary(d))
