import matplotlib
import matplotlib.pyplot as plt
from argparse import ArgumentParser
from invisibleroads_macros.disk import make_enumerated_folder_for, make_folder
from invisibleroads_macros.log import format_summary
from infrastructure_planning.exceptions import InvalidData
from infrastructure_planning.growth.interpolated import (
    get_interpolated_spline_extrapolated_linear_function)
from os.path import join
from pandas import DataFrame, isnull, read_csv
from six import string_types
from StringIO import StringIO


matplotlib.use('Agg')
DATASETS_FOLDER = 'datasets'
POPULATION_BY_YEAR_BY_COUNTRY_TABLE = read_csv(join(
    DATASETS_FOLDER, 'world-population-by-year-by-country.csv',
), encoding='utf-8')
ELECTRICITY_CONSUMPTION_PER_CAPITA_BY_YEAR_TABLE = read_csv(join(
    DATASETS_FOLDER, 'world-electricity-consumption-per-capita-by-year.csv',
), encoding='utf-8', skiprows=3)
COUNTRY_REGION_INCOME_TABLE = read_csv(StringIO(open(join(
    DATASETS_FOLDER, 'world-country-region-income.csv',
), 'r').read().decode('utf-8-sig')), encoding='utf-8')
COUNTRY_NAMES = []
ALTERNATE_COUNTRY_NAME_BY_COUNTRY_NAME = {}


def run(target_folder, target_year):
    d = []
    t = get_population_electricity_consumption_table(target_year)
    t_path = join(target_folder, 'electricity-consumption-by-population.csv')
    t.to_csv(t_path, encoding='utf-8', index=False)
    d.append(('electricity_consumption_by_population_table_path', t_path))
    # World
    d.extend(make_plots(target_folder, target_year, 'world', t))
    # Region
    for region_name, table in t.groupby('Region Name'):
        d.extend(make_plots(
            target_folder, target_year,
            _format_label_for_region(region_name), table))
    # Income
    for income_group_name, table in t.groupby('Income Group Name'):
        d.extend(make_plots(
            target_folder, target_year,
            _format_label_for_income_group(income_group_name), table))
    return d


def get_population_electricity_consumption_table(target_year):
    population_electricity_consumption_packs = []
    for country_name in yield_country_name():
        try:
            population = estimate_population(target_year, country_name)
            electricity_consumption_per_capita = \
                estimate_electricity_consumption_per_capita(
                    target_year, country_name)
        except InvalidData as e:
            print('skipping %s: %s' % (country_name.encode('utf-8'), e))
            continue
        electricity_consumption = \
            electricity_consumption_per_capita * population
        population_electricity_consumption_packs.append((
            country_name,
            get_region_name_for(country_name),
            get_income_group_name_for(country_name),
            target_year,
            population,
            electricity_consumption_per_capita,
            electricity_consumption))
    return DataFrame(population_electricity_consumption_packs, columns=[
        'Country Name',
        'Region Name',
        'Income Group Name',
        'Year',
        'Population',
        'Electricity Consumption Per Capita (kWh)',
        'Electricity Consumption (kWh)',
    ])


def make_plots(target_folder, target_year, label, table):
    return [
        _plot_against_population(
            target_folder, target_year, label, table,
            'electricity_consumption',
            'Electricity Consumption (kWh)'),
        _plot_against_population(
            target_folder, target_year, label, table,
            'electricity_consumption_per_capita',
            'Electricity Consumption Per Capita (kWh)'),
    ]


def yield_country_name():
    if not COUNTRY_NAMES:
        _prepare_country_names()
    return iter(COUNTRY_NAMES)


def estimate_population(target_year, country_name):
    t = POPULATION_BY_YEAR_BY_COUNTRY_TABLE
    country_t = _get_country_table(t, 'Country or Area', country_name)
    try:
        earliest_estimated_year = min(country_t[
            country_t['Variant'] == 'Low variant']['Year(s)'])
    except ValueError:
        raise InvalidData('missing population')
    # Get actual population for each year
    year_packs = country_t[country_t['Year(s)'] < earliest_estimated_year][[
        'Year(s)', 'Value']].values
    # Estimate population for the given year
    estimate_population = get_interpolated_spline_extrapolated_linear_function(
        year_packs)
    return estimate_population(target_year)


def estimate_electricity_consumption_per_capita(target_year, country_name):
    t = ELECTRICITY_CONSUMPTION_PER_CAPITA_BY_YEAR_TABLE
    country_t = _get_country_table(t, 'Country Name', country_name)
    if not len(country_t):
        raise InvalidData('missing country_name')
    year_packs = []
    for column_name in country_t.columns:
        try:
            year = int(column_name)
        except ValueError:
            continue
        value = country_t[column_name].values[0]
        if isnull(value):
            continue
        year_packs.append((year, value))
    if not year_packs:
        raise InvalidData('missing year_value')
    estimate_electricity_consumption_per_capita = \
        get_interpolated_spline_extrapolated_linear_function(year_packs)
    return estimate_electricity_consumption_per_capita(target_year)


def get_region_name_for(country_name):
    t = COUNTRY_REGION_INCOME_TABLE
    country_t = _get_country_table(t, 'Country Name', country_name)
    return country_t['Region'].values[0]


def get_income_group_name_for(country_name):
    t = COUNTRY_REGION_INCOME_TABLE
    country_t = _get_country_table(t, 'Country Name', country_name)
    return country_t['IncomeGroup'].values[0]


def _plot_against_population(
        target_folder, target_year, label, table, prefix, column):
    variable_nickname = ('%s-for-%s' % (prefix, label)).replace('_', '-')
    variable_name = variable_nickname.replace('-', '_') + '_image_path'
    target_path = join(target_folder, variable_nickname + '.jpg')
    xs = table['Population'].values
    ys = table[column].values
    zs = table['Country Name']
    figure = plt.figure()
    ax = figure.add_subplot(111)
    ax.scatter(xs, ys)
    ax.set_xlabel('Population')
    ax.set_ylabel(column)
    ax.set_xlim(left=0)
    ax.set_ylim(bottom=0)
    ax.set_title(_get_plot_title(label) + ' in %s' % target_year)
    for index, country_name in enumerate(zs):
        ax.annotate(country_name, (xs[index], ys[index]))
    figure.savefig(target_path)
    plt.close(figure)
    return variable_name, target_path


def _get_plot_title(x):
    x = x.replace('region', 'Region:')
    x = x.replace('income', 'Income Group:')
    x = x.replace('-', ' ')
    x = x.title()
    x = x.replace('Non Oecd', 'non-OECD')
    x = x.replace('Oecd', 'OECD')
    x = x.replace('And', 'and')
    return x


def _prepare_country_names():
    global COUNTRY_NAMES
    global ALTERNATE_COUNTRY_NAME_BY_COUNTRY_NAME
    country_name_table = read_csv(join(
        DATASETS_FOLDER, 'world-country-name.csv',
    ), encoding='utf-8', header=None)
    for index, row in country_name_table.iterrows():
        country_name = row[0]
        COUNTRY_NAMES.append(country_name)
        for alternate_country_name in row[1:]:
            if not isinstance(alternate_country_name, string_types):
                continue
            ALTERNATE_COUNTRY_NAME_BY_COUNTRY_NAME[
                country_name] = alternate_country_name
            ALTERNATE_COUNTRY_NAME_BY_COUNTRY_NAME[
                alternate_country_name] = country_name
            country_name = alternate_country_name


def _get_country_table(table, column_name, country_name):
    country_t = DataFrame()
    country_names = []
    while not len(country_t):
        country_t = table[table[column_name] == country_name]
        country_names.append(country_name)
        try:
            country_name = _get_alternate_country_name(country_name)
        except KeyError:
            break
        if country_name in country_names:
            break
    return country_t


def _get_alternate_country_name(country_name):
    if not ALTERNATE_COUNTRY_NAME_BY_COUNTRY_NAME:
        _prepare_country_names()
    return ALTERNATE_COUNTRY_NAME_BY_COUNTRY_NAME[country_name]


def _format_label_for_region(region_name):
    x = region_name.lower()
    x = x.replace(' ', '-')
    x = x.replace('&', 'and')
    return 'region-%s' % x


def _format_label_for_income_group(income_group_name):
    x = income_group_name.lower()
    x = x.replace(' ', '-')
    x = x.replace(':', '')
    x = x.replace('non', 'non-')
    x = x.replace('-income', '')
    return 'income-group-%s' % x


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
    print(format_summary(d))
