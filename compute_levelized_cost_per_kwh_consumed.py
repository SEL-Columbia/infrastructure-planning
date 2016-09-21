"""
from argparse import ArgumentParser
from infrastructure_planning.finance.valuation import (
    compute_levelized_cost_per_kwh_consumed)
from invisibleroads_macros.log import format_summary
from pandas import read_csv


def run(
        period_cost_table, period_column, production_cost_column,
        consumption_column, discount_rate_percent):

    levelized_cost_per_kwh_consumed = compute_levelized_cost_per_kwh_consumed(
        period_cost_table[[period_column, production_column, cost_column]].values, discount_rate_percent)

def compute_levelized_cost(time_production_cost_packs, discount_rate_percent):
    # TODO: Rename time to period
    time_production_cost_array = np.array(time_production_cost_packs)
    time_production_packs = time_production_cost_array[:, [0, 1]]
    time_cost_packs = time_production_cost_array[:, [0, 2]]

    discounted_cost = compute_discounted_cash_flow_xxx(
        time_cost_packs, discount_rate_percent)
    discounted_production = compute_discounted_cash_flow_xxx(
        time_production_packs, discount_rate_percent)

    return discounted_cost / discounted_production



    return [
        ('levelized_cost_per_kwh_consumed', levelized_cost_per_kwh_consumed),
    ]


if __name__ == '__main__':
    argument_parser = ArgumentParser()

    argument_parser.add_argument(
        '--period_cost_table_path',
        metavar='PATH', required=True)
    argument_parser.add_argument(
        '--period_cost_table_period_column',
        metavar='COLUMN', required=True)
    argument_parser.add_argument(
        '--period_cost_table_production_cost_column',
        metavar='COLUMN', required=True)
    argument_parser.add_argument(
        '--period_cost_table_consumption_column',
        metavar='COLUMN', required=True)

    argument_parser.add_argument(
        '--discount_rate_percent',
        metavar='PERCENT', type=float, required=True)

    args = argument_parser.parse_args()
    d = run(
        read_csv(args.period_cost_table_path),
        args.period_cost_table_period_column,
        args.period_cost_table_production_cost_column,
        args.period_cost_table_consumption_column,
        args.discount_rate_percent)
    print(format_summary(d))
"""
