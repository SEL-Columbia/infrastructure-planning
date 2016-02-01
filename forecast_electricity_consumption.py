import numpy as np
from argparse import ArgumentParser
from infrastructure_planning.exceptions import EmptyDataset
from infrastructure_planning.growth.interpolated import (
    get_interpolated_spline_extrapolated_linear_function)
from invisibleroads_macros.disk import make_enumerated_folder_for, make_folder
from os.path import join
from pandas import DataFrame, read_csv
from StringIO import StringIO


DATASETS_FOLDER = 'datasets'
COUNTRY_NAME_VARIATION_TABLE = read_csv(join(
    DATASETS_FOLDER, 'world-country-name-variation.csv'))
COUNTRY_REGION_INCOME_TABLE = read_csv(StringIO(open(join(
    DATASETS_FOLDER, 'world-country-region-income.csv',
), 'r').read().decode('utf-8-sig')))
POPULATION_BY_YEAR_BY_COUNTRY_TABLE = read_csv(join(
    DATASETS_FOLDER, 'world-population-by-year-by-country.csv'))
ELECTRICITY_CONSUMPTION_PER_CAPITA_BY_YEAR_TABLE = read_csv(join(
    DATASETS_FOLDER, 'world-electricity-consumption-per-capita-by-year.csv',
), skiprows=3)
UNITED_NATIONS_COUNTRY_NAMES = POPULATION_BY_YEAR_BY_COUNTRY_TABLE[
    'Country or Area'].unique()
WORLD_BANK_COUNTRY_NAMES = COUNTRY_REGION_INCOME_TABLE[
    'Country Name'].unique()


def run(target_folder, target_year):
    d = {}
    electricity_consumption_by_population_table_path = join(
        target_folder, 'electricity-consumption-by-population.csv')
    t = get_population_electricity_consumption_table(target_year)
    t.to_csv(electricity_consumption_by_population_table_path, index=False)
    d.append((
        'electricity_consumption_by_population_table_path',
        electricity_consumption_by_population_table_path))
    """
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
    """
    return d


def get_population_electricity_consumption_table(target_year):
    population_electricity_consumption_packs = []
    for united_nations_country_name in UNITED_NATIONS_COUNTRY_NAMES:
        try:
            world_bank_country_name = get_world_bank_country_name(
                united_nations_country_name)
        except ValueError:
            continue
        population = estimate_population(
            target_year, united_nations_country_name)
        try:
            electricity_consumption_per_capita = \
                estimate_electricity_consumption_per_capita(
                    target_year, world_bank_country_name)
        except EmptyDataset:
            continue
        electricity_consumption = \
            electricity_consumption_per_capita * population
        population_electricity_consumption_packs.append((
            population,
            electricity_consumption_per_capita,
            electricity_consumption))
    return DataFrame(population_electricity_consumption_packs, columns=[
        'Population',
        'Electricity Consumption Per Capita (kWh)',
        'Electricity Consumption (kWh)',
    ])


def estimate_population(target_year, united_nations_country_name):
    t = POPULATION_BY_YEAR_BY_COUNTRY_TABLE
    country_t = t[t['Country or Area'] == united_nations_country_name]
    earliest_estimated_year = min(country_t[
        country_t['Variant'] == 'Low variant']['Year(s)'])
    # Get actual populations
    year_packs = country_t[country_t['Year(s)'] < earliest_estimated_year][[
        'Year(s)', 'Value']].values
    # Estimate population for the given year
    estimate_population = get_interpolated_spline_extrapolated_linear_function(
        year_packs)
    return estimate_population(target_year)


def estimate_electricity_consumption_per_capita(
        target_year, world_bank_country_name):
    t = ELECTRICITY_CONSUMPTION_PER_CAPITA_BY_YEAR_TABLE
    print world_bank_country_name
    print repr(world_bank_country_name)
    country_t = t[t['Country Name'] == world_bank_country_name]
    """
    if not len(country_t):
        world_bank_country_name = get_alternate_country_name(
            world_bank_country_name)
        country_t = t[t['Country Name'] == world_bank_country_name]
    """
    year_packs = []
    for column_name in country_t.columns:
        try:
            year = int(column_name)
        except ValueError:
            continue
        value = country_t[column_name].values[0]
        if np.isnan(value):
            continue
        year_packs.append((year, value))
    estimate_electricity_consumption_per_capita = \
        get_interpolated_spline_extrapolated_linear_function(year_packs)
    return estimate_electricity_consumption_per_capita(target_year)


def plot_electricity_consumption_by_population(target_folder, label, table):
    variable_nickname = 'electricity_consumption_%s' % label
    variable_name = variable_nickname + '_image_path'
    target_path = join(
        target_folder, variable_nickname.replace('_', '-') + '.jpg')

    # Plot consumption vs population for the selected target_year

    return variable_name, target_path


def get_united_nations_country_name(world_bank_country_name):
    t = COUNTRY_NAME_VARIATION_TABLE
    try:
        return t[
            t['World Bank'] == world_bank_country_name
        ]['United Nations'].values[0]
    except IndexError:
        pass
    if world_bank_country_name not in UNITED_NATIONS_COUNTRY_NAMES:
        raise ValueError(world_bank_country_name)
    return world_bank_country_name


def get_world_bank_country_name(united_nations_country_name):
    t = COUNTRY_NAME_VARIATION_TABLE
    try:
        return t[
            t['United Nations'] == united_nations_country_name
        ]['World Bank'].values[0]
    except IndexError:
        pass
    if united_nations_country_name not in WORLD_BANK_COUNTRY_NAMES:
        raise ValueError(united_nations_country_name)
    return united_nations_country_name


def get_alternate_country_name(country_name):
    pass


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
