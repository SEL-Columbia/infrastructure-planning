import numpy as np
from collections import defaultdict
from importlib import import_module
from invisibleroads_macros.math import divide_safely
from itertools import product
from pandas import Series

from ...finance.valuation import compute_discounted_cash_flow
from ...macros import compute, get_by_prefix, get_final_value, get_first_value


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


def estimate_initial_and_recurring_cost(selected_technologies, **keywords):
    d = {}
    for technology in selected_technologies:
        local_cost_by_year = sum([
            keywords[technology + '_internal_cost_by_year'],
            keywords[technology + '_external_cost_by_year'],
        ])
        d[technology + '_local_cost_by_year'] = local_cost_by_year
        d[technology + '_local_initial_cost'] = get_first_value(
            local_cost_by_year)
        d[technology + '_local_recurring_cost'] = get_final_value(
            local_cost_by_year)
    return d


def estimate_discounted_cost(selected_technologies, **keywords):
    d = {}
    for technology in selected_technologies:
        d[technology + '_local_discounted_cost'] = sum([
            keywords[technology + '_internal_discounted_cost'],
            keywords[technology + '_external_discounted_cost']])
    return d


def estimate_levelized_cost(
        selected_technologies, discounted_consumption_in_kwh, **keywords):
    d = {}
    for technology in selected_technologies:
        discounted_cost = keywords[technology + '_local_discounted_cost']
        d[technology + '_local_levelized_cost_per_kwh_consumed'] = \
            divide_safely(discounted_cost, discounted_consumption_in_kwh, 0)
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
        d.update(compute(f, keywords))
    electricity_production_in_kwh_by_year = d.get(
        'electricity_production_in_kwh_by_year', zero_by_year)
    electricity_production_cost_by_year = d.get(
        'electricity_production_cost_by_year', zero_by_year)
    internal_distribution_cost_by_year = d.get(
        'internal_distribution_cost_by_year', zero_by_year)
    internal_cost_by_year = sum([
        electricity_production_cost_by_year,
        internal_distribution_cost_by_year])
    discounted_cost = compute_discounted_cash_flow(
        internal_cost_by_year, keywords['financing_year'],
        keywords['discount_rate_as_percent_of_cash_flow_per_year'])
    levelized_cost = divide_safely(discounted_cost, keywords[
        'discounted_consumption_in_kwh'], 0)
    # Record
    d['final_electricity_production_in_kwh_per_year'] = get_final_value(
        electricity_production_in_kwh_by_year)
    d['final_electricity_production_cost_per_year'] = get_final_value(
        electricity_production_cost_by_year)
    d['final_internal_distribution_cost_per_year'] = get_final_value(
        internal_distribution_cost_by_year)
    # Summarize
    d['internal_cost_by_year'] = internal_cost_by_year
    d['internal_discounted_cost'] = discounted_cost
    d['internal_levelized_cost_per_kwh_consumed'] = levelized_cost
    return d


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
        d.update(compute(f, keywords))
    external_distribution_cost_by_year = d.get(
        'external_distribution_cost_by_year', zero_by_year)
    external_cost_by_year = sum([
        external_distribution_cost_by_year])
    discounted_cost = compute_discounted_cash_flow(
        external_cost_by_year, keywords['financing_year'],
        keywords['discount_rate_as_percent_of_cash_flow_per_year'])
    # Record
    d['final_external_distribution_cost_per_year'] = get_final_value(
        external_distribution_cost_by_year)
    # Summarize
    d['external_cost_by_year'] = external_cost_by_year
    d['external_discounted_cost'] = discounted_cost
    return d
