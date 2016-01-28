from argparse import ArgumentParser
from invisibleroads_macros.disk import make_enumerated_folder_for, make_folder
from os.path import join


def run(target_folder, target_year):
    d = {}
    electricity_consumption_by_population_table_path = join(
        target_folder, 'electricity-consumption-by-population.csv')
    t = get_population_electricity_consumption_table(target_year)
    t.to_csv(electricity_consumption_by_population_table_path, index=False)
    d.append((
        'electricity_consumption_by_population_table_path',
        electricity_consumption_by_population_table_path))
    # World
    d.append(plot_electricity_consumption_by_population(
        target_folder, 'world', t))
    # Region
    for region_name, table in t.groupby('region_name'):
        d.append(plot_electricity_consumption_by_population(
            target_folder, _format_label_for_region(
                region_name), table))
    # Income
    for income_group_name, table in t.groupby('income_group_name'):
        d.append(plot_electricity_consumption_by_population(
            target_folder, _format_label_for_income_group(
                income_group_name), table))
    return d


def get_population_electricity_consumption_table(target_year):
    # Get countries
    # For each country, get projected population
    # Get the lowest year for which we have only estimates
    # Exclude all estimates
    # For each country, get projected consumption
    # by multiplying projected population by projected consumption per capita
    pass


def plot_electricity_consumption_by_population(target_folder, label, table):
    variable_nickname = 'electricity_consumption_%s' % label
    variable_name = variable_nickname + '_image_path'
    target_path = join(
        target_folder, variable_nickname.replace('_', '-') + '.jpg')

    # Plot consumption vs population for the selected target_year

    return variable_name, target_path


def _format_label_for_region(region_name):
    pass


def _format_label_for_income_group(income_group_name):
    pass


if __name__ == '__main__':
    argument_parser = ArgumentParser()
    argument_parser.add_argument(
        '--target_folder',
        metavar='FOLDER', type=make_folder)
    argument_parser.add_argument(
        '--target_year',
        metavar='YEAR', type=int, required=True)

    args = argument_parser.parse_args()
    d = run(
        args.target_folder or make_enumerated_folder_for(__file__),
        args.target_year)
