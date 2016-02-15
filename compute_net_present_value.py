from argparse import ArgumentParser
from crosscompute_table import TableType
from dateutil.parser import parse as parse_date
from invisibleroads_macros.log import format_summary


def run(time_value_table, time_column, value_column, interest_rate_percent):
    time_value_packs = sort_time_packs(time_value_table[[
        time_column, value_column]].values)
    net_present_value = compute_net_present_value(
        time_value_packs, interest_rate_percent)
    break_even_time = compute_break_even_time(time_value_packs)
    return [
        ('net_present_value', net_present_value),
        ('start_time', time_value_packs[0][0]),
        ('break_even_time', break_even_time),
    ]


def compute_net_present_value(time_value_packs, interest_rate_percent):
    time_value_packs = sort_time_packs(time_value_packs)
    interest_rate_factor = 1 + interest_rate_percent / 100.
    values = [value for time, value in time_value_packs]
    return sum(x / interest_rate_factor ** t for t, x in enumerate(values))


def compute_break_even_time(time_value_packs):
    time_value_packs = sort_time_packs(time_value_packs)
    for end_index in xrange(1, len(time_value_packs) + 1):
        net_present_value = compute_net_present_value(
            time_value_packs[:end_index])
        if net_present_value >= 0:
            break_even_time = time_value_packs[end_index - 1][0]
            break
    else:
        break_even_time = None
    return break_even_time


def sort_time_packs(time_packs):
    return sorted(time_packs, key=lambda x: parse_date(str(x[0])))


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
        '--interest_rate_percent',
        metavar='PERCENT', type=float, required=True)

    args = argument_parser.parse_args()
    d = run(
        TableType.load(args.time_value_table_path),
        args.time_value_table_time_column,
        args.time_value_table_value_column,
        args.interest_rate_percent)
    print(format_summary(d))
