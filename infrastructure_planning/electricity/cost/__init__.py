import numpy as np
from collections import defaultdict
from importlib import import_module
from invisibleroads_macros.math import divide_safely
from itertools import product
from pandas import Series

from ...finance.valuation import compute_discounted_cash_flow
from ...macros import compute, get_by_prefix


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


def prepare_component_cost_by_year(component_packs, keywords, prefix):
    d = {}
    cost_by_year_index = np.zeros(keywords['time_horizon_in_years'] + 1)
    for component, estimate_component_cost in component_packs:
        component_prefix = prefix + component + '_'
        v_by_k = compute(
            estimate_component_cost, keywords, d, prefix=component_prefix)
        # Add initial costs
        cost_by_year_index[0] += \
            get_by_prefix(v_by_k, component_prefix + 'installation')
        # Add recurring costs
        cost_by_year_index[1:] += \
            get_by_prefix(v_by_k, component_prefix + 'maintenance') + \
            get_by_prefix(v_by_k, component_prefix + 'replacement')
        # Save
        d.update(v_by_k)
    years = keywords['population_by_year'].index
    d['cost_by_year'] = Series(cost_by_year_index, index=years)
    return d


def prepare_internal_cost(functions, keywords):
    """
    Each function must return a dictionary with these keys:
        electricity_production_cost_by_year
        electricity_internal_distribution_cost_by_year

    The keywords dictionary must contain these keys:
        financing_year
        discount_rate_as_percent_of_cash_flow_per_year
        discounted_consumption_in_kwh
    """
    d = {}
    # Compute
    for f in functions:
        d.update(compute(f, keywords))
    cost_by_year = sum([
        d['electricity_production_cost_by_year'],
        d['electricity_internal_distribution_cost_by_year'],
    ])
    discounted_cost = compute_discounted_cash_flow(
        cost_by_year, keywords['financing_year'],
        keywords['discount_rate_as_percent_of_cash_flow_per_year'])
    levelized_cost = divide_safely(discounted_cost, keywords[
        'discounted_consumption_in_kwh'], 0)
    # Summarize
    d['internal_discounted_cost'] = discounted_cost
    d['internal_levelized_cost_per_kwh_consumed'] = levelized_cost
    return d
