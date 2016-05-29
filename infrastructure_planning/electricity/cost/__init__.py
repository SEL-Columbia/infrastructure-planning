import numpy as np
from collections import OrderedDict
from importlib import import_module
from invisibleroads_macros.iterable import OrderedDefaultDict
from itertools import product
from pandas import Series

from ...finance.valuation import compute_discounted_cash_flow
from ...macros import compute, get_by_prefix, rename_keys


def estimate_internal_cost_by_technology(selected_technologies, **keywords):
    'Estimate internal cost for each technology independently'
    # Compute
    d = OrderedDefaultDict(OrderedDict)
    for technology in selected_technologies:
        technology_module = import_module('%s.%s' % (__package__, technology))
        f = technology_module.estimate_internal_cost
        value_by_key = OrderedDict(compute(f, keywords))
        d.update(rename_keys(value_by_key, prefix=technology + '_'))
    # Summarize
    keys = [
        'internal_discounted_cost',
        'internal_levelized_cost',
    ]
    for technology, k in product(selected_technologies, keys):
        d['%s_by_technology' % k][technology] = d['%s_%s' % (technology, k)]
    return d


def estimate_external_cost_by_technology(selected_technologies, **keywords):
    'Estimate external cost for each technology independently'
    # Compute
    d = OrderedDefaultDict(OrderedDict)
    for technology in selected_technologies:
        technology_module = import_module('%s.%s' % (__package__, technology))
        f = technology_module.estimate_external_cost
        value_by_key = OrderedDict(compute(f, keywords))
        d.update(rename_keys(value_by_key, prefix=technology + '_'))
    # Summarize
    keys = [
        'external_discounted_cost',
    ]
    for technology, k in product(selected_technologies, keys):
        d['%s_by_technology' % k][technology] = d['%s_%s' % (technology, k)]
    return d


def prepare_component_cost_by_year(component_packs, keywords, prefix):
    d = OrderedDict()
    cost_by_year_index = np.zeros(keywords['time_horizon_in_years'] + 1)
    for component, estimate_component_cost in component_packs:
        v_by_k = OrderedDict(compute(estimate_component_cost, keywords, d))
        # Add initial costs
        cost_by_year_index[0] += get_by_prefix(v_by_k, 'installation')
        # Add recurring costs
        cost_by_year_index[1:] += \
            get_by_prefix(v_by_k, 'maintenance') + \
            get_by_prefix(v_by_k, 'replacement')
        # Save
        d.update(rename_keys(v_by_k, prefix=prefix + component + '_'))
    years = keywords['population_by_year'].index
    d['cost_by_year'] = Series(cost_by_year_index, index=years)
    return d


def prepare_internal_cost(functions, keywords):
    d = OrderedDict()
    # Compute
    for f in functions:
        d.update(compute(f, keywords))
    cost_by_year = sum([
        d['electricity_production_cost_by_year'],
        d['electricity_internal_distribution_cost_by_year'],
    ])
    financing_year = keywords['financing_year']
    discount_rate = keywords['discount_rate_as_percent_of_cash_flow_per_year']
    discounted_production_in_kwh = compute_discounted_cash_flow(
        d['electricity_production_in_kwh_by_year'],
        financing_year, discount_rate)
    discounted_cost = compute_discounted_cash_flow(
        cost_by_year, financing_year, discount_rate)
    levelized_cost = discounted_cost / float(discounted_production_in_kwh)
    d['electricity_discounted_production_in_kwh'] = \
        discounted_production_in_kwh
    # Summarize
    d['internal_discounted_cost'] = discounted_cost
    d['internal_levelized_cost'] = levelized_cost
    return d


def prepare_lv_line_cost(
        maximum_connection_count,
        line_length_adjustment_factor,
        average_distance_between_buildings_in_meters,
        lv_line_installation_lm_cost_per_meter,
        lv_line_maintenance_lm_cost_per_meter_per_year,
        lv_line_lifetime_in_years):
    # TODO: Compute lv line cost by year as connections come online
    line_length_in_meters = average_distance_between_buildings_in_meters * (
        maximum_connection_count - 1) * line_length_adjustment_factor
    installation_lm_cost = line_length_in_meters * \
        lv_line_installation_lm_cost_per_meter
    maintenance_lm_cost_per_year = line_length_in_meters * \
        lv_line_maintenance_lm_cost_per_meter_per_year
    replacement_lm_cost_per_year = \
        installation_lm_cost / float(lv_line_lifetime_in_years)
    return [
        ('installation_lm_cost', installation_lm_cost),
        ('maintenance_lm_cost_per_year', maintenance_lm_cost_per_year),
        ('replacement_lm_cost_per_year', replacement_lm_cost_per_year),
    ]


def prepare_lv_connection_cost(
        maximum_connection_count,
        lv_connection_installation_lm_cost_per_connection,
        lv_connection_maintenance_lm_cost_per_connection_per_year,
        lv_connection_lifetime_in_years):
    # TODO: Compute lv connection cost by year as connections come online
    installation_lm_cost = maximum_connection_count * \
        lv_connection_installation_lm_cost_per_connection
    maintenance_lm_cost_per_year = maximum_connection_count * \
        lv_connection_maintenance_lm_cost_per_connection_per_year
    replacement_lm_cost_per_year = \
        installation_lm_cost / float(lv_connection_lifetime_in_years)
    return [
        ('installation_lm_cost', installation_lm_cost),
        ('maintenance_lm_cost_per_year', maintenance_lm_cost_per_year),
        ('replacement_lm_cost_per_year', replacement_lm_cost_per_year),
    ]
