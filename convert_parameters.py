from argparse import ArgumentParser
from invisibleroads_macros.disk import make_enumerated_folder_for, make_folder
from invisibleroads_macros.log import format_summary
from pandas import read_csv


def run(target_folder, metrics_local_table_path):
    source_proj4 = open(metrics_local_table_path).next().strip()
    source_table = read_csv(args.metrics_local_table_path, header=1)
    return {}


if __name__ == '__main__':
    argument_parser = ArgumentParser()
    argument_parser.add_argument(
        '--target_folder',
        metavar='FOLDER', type=make_folder)

    argument_parser.add_argument(
        '--metrics_local_table_path',
        metavar='PATH', required=True)

    args = argument_parser.parse_args()
    d = run(
        args.target_folder or make_enumerated_folder_for(__file__),
        args.metrics_local_table_path)
    print(format_summary(d))
