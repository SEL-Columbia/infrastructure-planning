from argparse import ArgumentParser
from invisibleroads_macros.log import format_summary
from pandas import read_csv

from infrastructure_planning.finance.valuation import (
    compute_discounted_cash_flow_xxx,
    compute_break_even_time,
    compute_internal_return_rate)


def run(
        time_value_table,
        time_column, value_column,
        discount_rate_percent):
    time_value_packs = time_value_table[[time_column, value_column]].values
    discounted_cash_flow = compute_discounted_cash_flow_xxx(
        time_value_packs, discount_rate_percent)
    break_even_time = compute_break_even_time(
        time_value_packs, discount_rate_percent)
    internal_return_rate = compute_internal_return_rate(
        time_value_packs)
    return [
        ('discounted_cash_flow', discounted_cash_flow),
        ('start_time', time_value_packs[0][0]),
        ('break_even_time', break_even_time),
        ('internal_return_rate', internal_return_rate),
    ]


if __name__ == '__main__':
    argument_parser = ArgumentParser()

    argument_parser.add_argument(
        '--time_value_table_path',
        metavar='PATH', required=True)
    argument_parser.add_argument(
        '--time_value_table_time_column',
        metavar='COLUMN', required=True)
    argument_parser.add_argument(
        '--time_value_table_value_column',
        metavar='COLUMN', required=True)

    argument_parser.add_argument(
        '--discount_rate_percent',
        metavar='PERCENT', type=float, required=True)

    args = argument_parser.parse_args()
    d = run(
        read_csv(args.time_value_table_path),
        args.time_value_table_time_column,
        args.time_value_table_value_column,
        args.discount_rate_percent)
    print(format_summary(d))
