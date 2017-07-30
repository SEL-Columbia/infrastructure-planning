import numpy as np
from collections import defaultdict
from importlib import import_module
from invisibleroads_macros.calculator import divide_safely
from invisibleroads_macros.iterable import merge_dictionaries
from itertools import product
from pandas import Series

from ...finance.valuation import compute_discounted_cash_flow
from ...macros import compute, get_by_prefix, get_final_value, sum_by_suffix


def estimate_internal_cost_by_technology(selected_technologies, **keywords):
    'Estimate internal cost for each technology independently'
    # Compute
    d = defaultdict(dict)
    for technology in selected_technologies:
        technology_module = import_module('%s.%s' % (__package__, technology))
        f = technology_module.estimate_internal_cost
        d.update(compute(f, keywords, prefix=technology + '_'))
    # Summarize
    keys = [
        'internal_discounted_cost',
        'internal_levelized_cost_per_kwh_consumed',
    ]
    for technology, k in product(selected_technologies, keys):
        d['%s_by_technology' % k][technology] = d['%s_%s' % (technology, k)]
    return d


def estimate_external_cost_by_technology(selected_technologies, **keywords):
    'Estimate external cost for each technology independently'
    # Compute
    d = defaultdict(dict)
    for technology in selected_technologies:
        technology_module = import_module('%s.%s' % (__package__, technology))
        f = technology_module.estimate_external_cost
        d.update(compute(f, keywords, prefix=technology + '_'))
    # Summarize
    keys = [
        'external_discounted_cost',
    ]
    for technology, k in product(selected_technologies, keys):
        d['%s_by_technology' % k][technology] = d['%s_%s' % (technology, k)]
    return d


def estimate_cost_profile(selected_technologies, **keywords):
    d = {}
    suffixes = [
        '_initial_cost',
        '_recurring_fixed_cost_per_year',
        '_recurring_variable_cost_per_year',
        '_discounted_cost',
        '_levelized_cost_per_kwh_consumed',
    ]
    for technology in selected_technologies:
        for suffix in suffixes:
            d[technology + '_local' + suffix] = sum([
                keywords[technology + '_internal' + suffix],
                keywords[technology + '_external' + suffix],
            ])
    return d


def prepare_component_cost_by_year(component_packs, keywords, prefix):
    d = {}
    cost_by_year_index = np.zeros(keywords['time_horizon_in_years'] + 1)
    for component, estimate_component_cost in component_packs:
        component_prefix = prefix + component + '_'
        v_by_k = compute(
            estimate_component_cost, keywords, d, prefix=component_prefix)
        # Add initial costs
        cost_by_year_index[0] += \
            get_by_prefix(v_by_k, component_prefix + 'raw') + \
            get_by_prefix(v_by_k, component_prefix + 'installation')
        # Add recurring costs
        cost_by_year_index[1:] += \
            get_by_prefix(v_by_k, component_prefix + 'maintenance') + \
            get_by_prefix(v_by_k, component_prefix + 'replacement')
        # Save
        d.update(v_by_k)
    years = keywords['population_by_year'].index
    component_cost_by_year = Series(cost_by_year_index, index=years)
    return component_cost_by_year, d


def prepare_internal_cost(functions, keywords):
    """
    Each function can return a dictionary with these keys:
        system_capacity_cost_by_year
        electricity_production_in_kwh_by_year
        electricity_production_cost_by_year
        internal_distribution_cost_by_year

    The keywords dictionary must contain these keys:
        financing_year
        discount_rate_as_percent_of_cash_flow_per_year
        discounted_consumption_in_kwh
    """
    d = {}
    zero_by_year = keywords['zero_by_year']
    # Compute
    for f in functions:
        d.update(compute(f, d, keywords))
    system_capacity_cost_by_year = d.get(
        'system_capacity_cost_by_year', zero_by_year)
    electricity_production_in_kwh_by_year = d.get(
        'electricity_production_in_kwh_by_year', zero_by_year)
    electricity_production_cost_by_year = d.get(
        'electricity_production_cost_by_year', zero_by_year)
    internal_distribution_cost_by_year = d.get(
        'internal_distribution_cost_by_year', zero_by_year)
    cost_by_year = sum([
        system_capacity_cost_by_year,
        electricity_production_cost_by_year,
        internal_distribution_cost_by_year])
    # Record
    d['final_system_capacity_cost_per_year'] = get_final_value(
        system_capacity_cost_by_year)
    d['final_electricity_production_in_kwh_per_year'] = get_final_value(
        electricity_production_in_kwh_by_year)
    d['final_electricity_production_cost_per_year'] = get_final_value(
        electricity_production_cost_by_year)
    d['final_internal_distribution_cost_per_year'] = get_final_value(
        internal_distribution_cost_by_year)
    return prepare_cost_summary(cost_by_year, d, keywords, prefix='internal_')


def prepare_external_cost(functions, keywords):
    """
    Each function can return a dictionary with these keys:
        external_distribution_cost_by_year

    The keywords dictionary must contain these keys:
        financing_year
        discount_rate_as_percent_of_cash_flow_per_year
    """
    d = {}
    zero_by_year = keywords['zero_by_year']
    # Compute
    for f in functions:
        d.update(compute(f, d, keywords))
    external_distribution_cost_by_year = d.get(
        'external_distribution_cost_by_year', zero_by_year)
    cost_by_year = sum([
        external_distribution_cost_by_year])
    # Record
    d['final_external_distribution_cost_per_year'] = get_final_value(
        external_distribution_cost_by_year)
    return prepare_cost_summary(cost_by_year, d, keywords, prefix='external_')


def prepare_cost_summary(cost_by_year, d, keywords, prefix):
    """
    Summarize costs using the values provided in *d*
    """
    discounted_cost = compute_discounted_cash_flow(
        cost_by_year, keywords['financing_year'],
        keywords['discount_rate_as_percent_of_cash_flow_per_year'])
    levelized_cost = divide_safely(discounted_cost, keywords[
        'discounted_consumption_in_kwh'], 0)
    return merge_dictionaries(d, {
        prefix + 'cost_by_year': cost_by_year,
        prefix + 'initial_cost': sum([
            sum_by_suffix(d, '_raw_cost'),
            sum_by_suffix(d, '_installation_cost'),
        ]),
        prefix + 'recurring_fixed_cost_per_year': sum([
            sum_by_suffix(d, '_maintenance_cost_per_year'),
            sum_by_suffix(d, '_replacement_cost_per_year'),
        ]),
        prefix + 'recurring_variable_cost_per_year': sum([
            d.get('final_electricity_production_cost_per_year', 0),
        ]),
        prefix + 'discounted_cost': discounted_cost,
        prefix + 'levelized_cost_per_kwh_consumed': levelized_cost,
    })
