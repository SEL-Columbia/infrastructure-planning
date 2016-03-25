import inspect
import numpy as np
from argparse import ArgumentParser
from collections import OrderedDict
from crosscompute_table import TableType
from invisibleroads_macros.disk import make_enumerated_folder_for, make_folder
from invisibleroads_macros.iterable import (
    OrderedDefaultDict, merge_dictionaries)
from invisibleroads_macros.log import format_summary
from os.path import join
from pandas import DataFrame, MultiIndex, Series, concat

from infrastructure_planning.exceptions import InfrastructurePlanningError


def estimate_population_by_year(
        population,
        population_year,
        population_growth_as_percent_of_population_per_year,
        financing_year,
        time_horizon_in_years):
    # TODO: Support the case when financing_year is less than population_year
    if financing_year < population_year:
        raise InfrastructurePlanningError('financing_year', M[
            'bad_financing_year'] % (financing_year, population_year))
    # Compute the population at financing_year
    base_population = grow_exponentially(
        population, population_growth_as_percent_of_population_per_year,
        financing_year - population_year)
    # Compute the population over time_horizon_in_years
    year_increments = Series(range(time_horizon_in_years + 1))
    years = financing_year + year_increments
    populations = grow_exponentially(
        base_population, population_growth_as_percent_of_population_per_year,
        year_increments)
    populations.index = years
    return [
        ('population_by_year', populations),
    ]


def estimate_consumption_in_kwh_by_year(
        population_by_year,
        connection_count_per_thousand_people,
        consumption_per_connection_in_kwh):
    t = DataFrame({'population': population_by_year})
    t['connection_count'] = connection_count_per_thousand_people * t[
        'population'] / 1000.
    t['consumption_in_kwh'] = consumption_per_connection_in_kwh * t[
        'connection_count']
    return [
        ('connection_count_by_year', t['connection_count']),
        ('consumption_in_kwh_by_year', t['consumption_in_kwh']),
    ]


def estimate_peak_demand_in_kw(
        consumption_in_kwh_by_year,
        consumption_during_peak_hours_as_percent_of_total_consumption,
        peak_hours_of_consumption_per_year):
    maximum_consumption_per_year_in_kwh = consumption_in_kwh_by_year.max()
    consumption_during_peak_hours_in_kwh = \
        maximum_consumption_per_year_in_kwh * \
        consumption_during_peak_hours_as_percent_of_total_consumption / 100.
    peak_demand_in_kw = consumption_during_peak_hours_in_kwh / float(
        peak_hours_of_consumption_per_year)
    return [
        ('peak_demand_in_kw', peak_demand_in_kw),
    ]


def estimate_system_cost_by_technology(**kw):
    'Estimate system cost for each technology independently'
    keys = [
        'discounted_system_cost',
        'levelized_system_cost',
    ]
    d = OrderedDefaultDict(OrderedDict)
    for technology, estimate_system_cost in [
        ('grid', estimate_grid_system_cost),
        # ('diesel_mini_grid', estimate_diesel_mini_grid_system_cost),
        # ('solar_home', estimate_solar_home_system_cost),
    ]:
        v_by_k = OrderedDict(compute(estimate_system_cost, kw))
        d.update(('%s_%s' % (technology, k), v) for k, v in v_by_k.items())
        for key in keys:
            d['%s_by_technology' % key][technology] = v_by_k[key]
    return d


def estimate_grid_system_cost(**kw):
    return prepare_system_cost([
        estimate_grid_electricity_production_cost,
        estimate_grid_electricity_distribution_cost,
    ], kw)


def estimate_grid_electricity_production_cost(
        consumption_in_kwh_by_year,
        grid_system_loss_as_percent_of_total_production,
        grid_medium_voltage_transformer_load_power_factor,
        grid_electricity_production_cost_per_kwh):
    if not -1 <= grid_medium_voltage_transformer_load_power_factor <= 1:
        raise InfrastructurePlanningError(
            'grid_medium_voltage_transformer_load_power_factor', M[
                'bad_power_factor'
            ] % grid_medium_voltage_transformer_load_power_factor)
    production_in_kwh_by_year = adjust_for_losses(
        consumption_in_kwh_by_year,
        grid_system_loss_as_percent_of_total_production / 100.,
        1 - grid_medium_voltage_transformer_load_power_factor)
    d = OrderedDict()
    d['electricity_production_in_kwh_by_year'] = production_in_kwh_by_year
    d['electricity_production_cost_by_year'] = \
        grid_electricity_production_cost_per_kwh * production_in_kwh_by_year
    return d


def estimate_grid_electricity_distribution_cost():
    d = OrderedDict()
    d['electricity_distribution_cost_by_year'] = Series()
    return d


def estimate_diesel_mini_grid_system_cost(**kw):
    return prepare_system_cost([
        estimate_diesel_mini_grid_electricity_production_cost,
        estimate_diesel_mini_grid_electricity_distribution_cost,
    ], kw)


def estimate_diesel_mini_grid_electricity_production_cost():
    d = OrderedDict()
    d['electricity_production_cost_by_year'] = Series()
    return d


def estimate_diesel_mini_grid_electricity_distribution_cost():
    d = OrderedDict()
    d['electricity_distribution_cost_by_year'] = Series()
    return d


def estimate_solar_home_system_cost(**kw):
    return prepare_system_cost([
        estimate_solar_home_electricity_production_cost,
        estimate_solar_home_electricity_distribution_cost,
    ], kw)


def estimate_solar_home_electricity_production_cost():
    d = OrderedDict()
    d['electricity_production_cost_by_year'] = Series()
    return d


def estimate_solar_home_electricity_distribution_cost():
    d = OrderedDict()
    d['electricity_distribution_cost_by_year'] = Series()
    return d


def prepare_system_cost(fs, kw):
    d = OrderedDict()
    # Compute
    for f in fs:
        d.update(compute(f, kw))
    d['system_cost_by_year'] = sum([
        d['electricity_production_cost_by_year'],
        d['electricity_distribution_cost_by_year'],
    ])
    financing_year = kw['financing_year']
    discount_rate = kw['discount_rate_as_percent_of_cash_flow_per_year']
    discounted_production_in_kwh = compute_discounted_cash_flow(
        d['electricity_production_in_kwh_by_year'],
        financing_year, discount_rate)
    discounted_cost = compute_discounted_cash_flow(
        d['system_cost_by_year'],
        financing_year, discount_rate)
    levelized_cost = discounted_cost / float(discounted_production_in_kwh)
    # Summarize
    d['discounted_electricity_production_in_kwh'] = \
        discounted_production_in_kwh
    d['discounted_system_cost'] = discounted_cost
    d['levelized_system_cost'] = levelized_cost
    return d


def estimate_network_budget(
        system_cost_by_technology):
    return []


def grow_exponentially(value, growth_as_percent, growth_count):
    return value * (1 + growth_as_percent / 100.) ** growth_count


def adjust_for_losses(x, *fractional_losses):

    def adjust_for_loss(x, fractional_loss):
        divisor = 1 - fractional_loss
        if not divisor:
            return x
        return x / float(divisor)

    y = x
    for fractional_loss in fractional_losses:
        y = adjust_for_loss(y, fractional_loss)
    return y


def compute_discounted_cash_flow(
        cash_flow_by_year, financing_year, discount_rate_as_percent):
    year_increments = np.array(cash_flow_by_year.index - financing_year)
    discount_rate_as_factor = 1 + discount_rate_as_percent / 100.
    return sum(cash_flow_by_year / discount_rate_as_factor ** year_increments)


def load_abbreviations(locale):
    return {
        'name': 'name',
        'population': 'population',
        'year': 'year',
    }


def load_messages(locale):
    return {
        'bad_financing_year': (
            'financing year (%s) must be greater than or equal to '
            'population year (%s)'),
        'bad_power_factor': 'power factor (%s) must be between -1 and 1',
    }


A = load_abbreviations('en-US')
M = load_messages('en-US')
FUNCTIONS = [
    estimate_population_by_year,
    estimate_consumption_in_kwh_by_year,
    estimate_peak_demand_in_kw,
    estimate_system_cost_by_technology,
    # estimate_network_budget,
]


def run(target_folder, g):
    # Prepare
    t = g['demographic_table']
    t.columns = normalize_column_names(t.columns, g['locale'])
    # Compute with node-level override
    l_by_name = OrderedDict()
    for name, table in t.groupby('name'):
        l = get_local_arguments(table)
        for f in FUNCTIONS:
            try:
                l.update(compute(f, l, g))
            except InfrastructurePlanningError as e:
                exit('%s.error = %s : %s : %s' % (
                    e[0], name.encode('utf-8'), f.func_name, e[1]))
        l_by_name[name] = l
    l_by_name, g = sift_common_values(l_by_name, g)
    # Add location information if it doesn't exist
    # Build the network

    # Save
    # save_common_values(target_folder, g)
    # save_unique_values(target_folder, l_by_name)
    save_yearly_values(target_folder, l_by_name)

    # Summarize
    d = OrderedDict()
    return d


def normalize_column_names(columns, locale):
    'Translate each column name into English'
    return [x.lower() for x in columns]


def get_local_arguments(table):
    'Convert the table into local arguments'
    # TODO: Support specifying different overrides for different years
    d = OrderedDict(table.ix[table.index[0]])
    d['population_year'] = d['year']  # Let year be population_year
    return d


def compute(f, l, g=None):
    'Compute the function using local arguments if possible'
    if not g:
        g = {}
    # If the function wants every argument, provide every argument
    argument_specification = inspect.getargspec(f)
    if argument_specification.keywords:
        return f(**merge_dictionaries(g, l))
    # Otherwise, provide only requested arguments
    kw = {}
    for argument_name in argument_specification.args:
        argument_value = l.get(argument_name, g.get(argument_name))
        if argument_value is None:
            raise KeyError(argument_name)
        kw[argument_name] = argument_value
    return f(**kw)


def sift_common_values(l_by_name, g):
    'Move local arguments with common values into global arguments'
    # TODO
    return l_by_name, g


def save_common_values(target_folder, g):
    pass


def save_unique_values(target_folder, l_by_name):
    pass


def save_yearly_values(target_folder, l_by_name):
    target_path = join(target_folder, 'yearly_values.csv')
    columns = OrderedDefaultDict(list)
    for name, l in l_by_name.items():
        for k, v in l.items():
            if not k.endswith('_by_year') or v.empty:
                continue
            column = Series(v)
            column.index = MultiIndex.from_tuples([(
                name, x) for x in column.index], names=[A['name'], A['year']])
            columns[k.replace('_by_year', '')].append(column)
    table = DataFrame()
    for name, columns in columns.items():
        table[name] = concat(columns)
    table.to_csv(target_path)
    return target_path


if __name__ == '__main__':
    argument_parser = ArgumentParser()
    argument_parser.add_argument(
        '--target_folder',
        metavar='FOLDER', type=make_folder)
    argument_parser.add_argument(
        '--locale',
        metavar='LOCALE', default='en-US')

    argument_parser.add_argument(
        '--financing_year',
        metavar='YEAR', required=True, type=int)
    argument_parser.add_argument(
        '--time_horizon_in_years',
        metavar='INTEGER', required=True, type=int)
    argument_parser.add_argument(
        '--discount_rate_as_percent_of_cash_flow_per_year',
        metavar='PERCENT', required=True, type=float)

    argument_parser.add_argument(
        '--demographic_table_path',
        metavar='PATH', required=True)
    argument_parser.add_argument(
        '--population_year',
        metavar='YEAR', required=True, type=int)
    argument_parser.add_argument(
        '--population_growth_as_percent_of_population_per_year',
        metavar='INTEGER', required=True, type=int)

    argument_parser.add_argument(
        '--connection_count_per_thousand_people',
        metavar='FLOAT', required=True, type=float)
    argument_parser.add_argument(
        '--consumption_per_connection_in_kwh',
        metavar='FLOAT', required=True, type=float)

    argument_parser.add_argument(
        '--consumption_during_peak_hours_as_percent_of_total_consumption',
        metavar='PERCENT', required=True, type=float)
    argument_parser.add_argument(
        '--peak_hours_of_consumption_per_year',
        metavar='FLOAT', required=True, type=float)

    argument_parser.add_argument(
        '--grid_system_loss_as_percent_of_total_production',
        metavar='PERCENT', required=True, type=float)
    argument_parser.add_argument(
        '--grid_medium_voltage_transformer_load_power_factor',
        metavar='FLOAT', required=True, type=float)
    argument_parser.add_argument(
        '--grid_electricity_production_cost_per_kwh',
        metavar='FLOAT', required=True, type=float)

    args = argument_parser.parse_args()
    A = load_abbreviations(args.locale)
    M = load_messages(args.locale)
    g = args.__dict__.copy()
    g['demographic_table'] = TableType.load(args.demographic_table_path)
    d = run(args.target_folder or make_enumerated_folder_for(__file__), g)
    print(format_summary(d))
