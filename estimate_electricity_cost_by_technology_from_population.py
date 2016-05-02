import geopy
import inspect
import numpy as np
from argparse import ArgumentParser
from collections import OrderedDict
from copy import copy, deepcopy
from invisibleroads_macros.disk import make_enumerated_folder_for, make_folder
from invisibleroads_macros.iterable import (
    OrderedDefaultDict, merge_dictionaries)
from invisibleroads_macros.log import format_summary
from itertools import product
from math import ceil
from networkx import Graph
from operator import mul
from os.path import join
from pandas import DataFrame, MultiIndex, Series, concat, read_csv
from shapely.geometry import Point, LineString

from infrastructure_planning.exceptions import InfrastructurePlanningError
from networker.networker_runner import NetworkerRunner
from sequencer import NetworkPlan
from sequencer.Models import EnergyMaximizeReturn


def estimate_nodal_population(
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


def estimate_nodal_consumption_in_kwh(
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


def estimate_nodal_peak_demand_in_kw(
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


def estimate_nodal_internal_cost_by_technology(**kw):
    'Estimate internal cost for each technology independently'
    # Compute
    d = OrderedDefaultDict(OrderedDict)
    for technology, estimate_cost in COST_FUNCTION_BY_TECHNOLOGY.items():
        value_by_key = OrderedDict(compute(estimate_cost, kw))
        d.update(rename_keys(value_by_key, prefix=technology + '_'))
    # Summarize
    keys = [
        'internal_discounted_cost',
        'internal_levelized_cost',
    ]
    for technology, k in product(COST_FUNCTION_BY_TECHNOLOGY, keys):
        d['%s_by_technology' % k][technology] = d['%s_%s' % (technology, k)]
    return d


def estimate_grid_internal_cost(**kw):
    return prepare_internal_cost([
        estimate_grid_electricity_production_cost,
        estimate_grid_electricity_internal_distribution_cost,
    ], kw)


def estimate_grid_electricity_production_cost(
        consumption_in_kwh_by_year,
        grid_system_loss_as_percent_of_total_production,
        grid_mv_transformer_load_power_factor,
        grid_electricity_production_cost_per_kwh):
    if not -1 <= grid_mv_transformer_load_power_factor <= 1:
        raise InfrastructurePlanningError(
            'grid_mv_transformer_load_power_factor', M[
                'bad_power_factor'
            ] % grid_mv_transformer_load_power_factor)
    production_in_kwh_by_year = adjust_for_losses(
        consumption_in_kwh_by_year,
        grid_system_loss_as_percent_of_total_production / 100.,
        1 - grid_mv_transformer_load_power_factor)
    d = OrderedDict()
    d['electricity_production_in_kwh_by_year'] = production_in_kwh_by_year
    d['electricity_production_cost_by_year'] = \
        grid_electricity_production_cost_per_kwh * production_in_kwh_by_year
    return d


def estimate_grid_electricity_internal_distribution_cost(**kw):
    d = prepare_component_cost_by_year([
        ('mv_transformer', estimate_grid_mv_transformer_cost),
        ('lv_line', estimate_grid_lv_line_cost),
        ('lv_connection', estimate_grid_lv_connection_cost),
    ], kw, prefix='grid_')
    d['electricity_internal_distribution_cost_by_year'] = d.pop('cost_by_year')
    return d


def estimate_grid_mv_transformer_cost(
        peak_demand_in_kw,
        grid_system_loss_as_percent_of_total_production,
        grid_mv_transformer_load_power_factor,
        grid_mv_transformer_table):
    # Estimate desired capacity
    desired_system_capacity_in_kva = adjust_for_losses(
        peak_demand_in_kw,
        grid_system_loss_as_percent_of_total_production / 100.,
        1 - grid_mv_transformer_load_power_factor)
    # Choose transformer type
    return prepare_actual_system_capacity(
        desired_system_capacity_in_kva,
        grid_mv_transformer_table, 'capacity_in_kva')


def estimate_grid_lv_line_cost(
        connection_count_by_year,
        average_distance_between_buildings_in_meters,
        grid_lv_line_installation_lm_cost_per_meter,
        grid_lv_line_maintenance_lm_cost_per_meter_per_year,
        grid_lv_line_lifetime_in_years):
    return prepare_lv_line_cost(
        connection_count_by_year,
        average_distance_between_buildings_in_meters,
        grid_lv_line_installation_lm_cost_per_meter,
        grid_lv_line_maintenance_lm_cost_per_meter_per_year,
        grid_lv_line_lifetime_in_years)


def estimate_grid_lv_connection_cost(
        connection_count_by_year,
        grid_lv_connection_installation_lm_cost_per_connection,
        grid_lv_connection_maintenance_lm_cost_per_connection_per_year,
        grid_lv_connection_lifetime_in_years):
    return prepare_lv_connection_cost(
        connection_count_by_year,
        grid_lv_connection_installation_lm_cost_per_connection,
        grid_lv_connection_maintenance_lm_cost_per_connection_per_year,
        grid_lv_connection_lifetime_in_years)


def estimate_grid_mv_line_cost_per_meter(
        grid_mv_line_installation_lm_cost_per_meter,
        grid_mv_line_maintenance_lm_cost_per_meter_per_year,
        grid_mv_line_lifetime_in_years):
    grid_mv_line_replacement_lm_cost_per_year_per_meter = \
        grid_mv_line_installation_lm_cost_per_meter / float(
            grid_mv_line_lifetime_in_years)
    return [
        ('installation_lm_cost_per_meter',
            grid_mv_line_installation_lm_cost_per_meter),
        ('maintenance_lm_cost_per_meter_per_year',
            grid_mv_line_maintenance_lm_cost_per_meter_per_year),
        ('replacement_lm_cost_per_meter_per_year',
            grid_mv_line_replacement_lm_cost_per_year_per_meter),
    ]


def estimate_diesel_mini_grid_internal_cost(**kw):
    return prepare_internal_cost([
        estimate_diesel_mini_grid_electricity_production_cost,
        estimate_diesel_mini_grid_electricity_internal_distribution_cost,
    ], kw)


def estimate_diesel_mini_grid_electricity_production_cost(**kw):
    d = prepare_component_cost_by_year([
        ('generator', estimate_diesel_mini_grid_generator_cost),
    ], kw, prefix='diesel_mini_grid_')
    d.update(compute(estimate_diesel_mini_grid_fuel_cost, kw, d))
    d['electricity_production_cost_by_year'] = d.pop('cost_by_year') + d[
        'diesel_mini_grid_fuel_cost_by_year']
    return d


def estimate_diesel_mini_grid_electricity_internal_distribution_cost(**kw):
    d = prepare_component_cost_by_year([
        ('lv_line', estimate_diesel_mini_grid_lv_line_cost),
        ('lv_connection', estimate_diesel_mini_grid_lv_connection_cost),
    ], kw, prefix='diesel_mini_grid_')
    d['electricity_internal_distribution_cost_by_year'] = d.pop('cost_by_year')
    return d


def estimate_diesel_mini_grid_generator_cost(
        peak_demand_in_kw,
        diesel_mini_grid_system_loss_as_percent_of_total_production,
        diesel_mini_grid_generator_table):
    # Estimate desired capacity
    desired_system_capacity_in_kw = adjust_for_losses(
        peak_demand_in_kw,
        diesel_mini_grid_system_loss_as_percent_of_total_production / 100.)
    # Choose generator type
    return prepare_actual_system_capacity(
        desired_system_capacity_in_kw,
        diesel_mini_grid_generator_table, 'capacity_in_kw')


def estimate_diesel_mini_grid_fuel_cost(
        consumption_in_kwh_by_year,
        diesel_mini_grid_generator_actual_system_capacity_in_kw,
        diesel_mini_grid_generator_minimum_hours_of_production_per_year,
        diesel_mini_grid_system_loss_as_percent_of_total_production,
        diesel_mini_grid_fuel_cost_per_liter,
        diesel_mini_grid_fuel_liters_consumed_per_kwh):
    d = OrderedDict()
    production_in_kwh_by_year = adjust_for_losses(
        consumption_in_kwh_by_year,
        diesel_mini_grid_system_loss_as_percent_of_total_production / 100.)
    desired_hours_of_production_by_year = production_in_kwh_by_year / float(
        diesel_mini_grid_generator_actual_system_capacity_in_kw)
    years = production_in_kwh_by_year.index
    minimum_hours_of_production_by_year = Series([
        diesel_mini_grid_generator_minimum_hours_of_production_per_year,
    ] * len(years), index=years)
    effective_hours_of_production_by_year = DataFrame({
        'desired': desired_hours_of_production_by_year,
        'minimum': minimum_hours_of_production_by_year,
    }).max(axis=1)
    d['diesel_mini_grid_effective_hours_of_production_by_year'] = \
        effective_hours_of_production_by_year
    d['diesel_mini_grid_fuel_cost_by_year'] = reduce(mul, [
        diesel_mini_grid_fuel_cost_per_liter,
        diesel_mini_grid_fuel_liters_consumed_per_kwh,
        diesel_mini_grid_generator_actual_system_capacity_in_kw,
        effective_hours_of_production_by_year,
    ], 1)
    d['electricity_production_in_kwh_by_year'] = production_in_kwh_by_year
    return d


def estimate_diesel_mini_grid_lv_line_cost(
        connection_count_by_year,
        average_distance_between_buildings_in_meters,
        diesel_mini_grid_lv_line_installation_lm_cost_per_meter,
        diesel_mini_grid_lv_line_maintenance_lm_cost_per_meter_per_year,
        diesel_mini_grid_lv_line_lifetime_in_years):
    return prepare_lv_line_cost(
        connection_count_by_year,
        average_distance_between_buildings_in_meters,
        diesel_mini_grid_lv_line_installation_lm_cost_per_meter,
        diesel_mini_grid_lv_line_maintenance_lm_cost_per_meter_per_year,
        diesel_mini_grid_lv_line_lifetime_in_years)


def estimate_diesel_mini_grid_lv_connection_cost(
        connection_count_by_year,
        diesel_mini_grid_lv_connection_installation_lm_cost_per_connection,
        diesel_mini_grid_lv_connection_maintenance_lm_cost_per_connection_per_year,  # noqa
        diesel_mini_grid_lv_connection_lifetime_in_years):
    return prepare_lv_connection_cost(
        connection_count_by_year,
        diesel_mini_grid_lv_connection_installation_lm_cost_per_connection,
        diesel_mini_grid_lv_connection_maintenance_lm_cost_per_connection_per_year,  # noqa
        diesel_mini_grid_lv_connection_lifetime_in_years)


def estimate_solar_home_internal_cost(**kw):
    return prepare_internal_cost([
        estimate_solar_home_electricity_production_cost,
        estimate_solar_home_electricity_internal_distribution_cost,
    ], kw)


def estimate_solar_home_electricity_production_cost(**kw):
    d = prepare_component_cost_by_year([
        ('panel', estimate_solar_home_panel_cost),
        ('battery', estimate_solar_home_battery_cost),
        ('balance', estimate_solar_home_balance_cost),
    ], kw, prefix='solar_home_')
    d['electricity_production_in_kwh_by_year'] = adjust_for_losses(
        kw['consumption_in_kwh_by_year'],
        kw['solar_home_system_loss_as_percent_of_total_production'] / 100.)
    d['electricity_production_cost_by_year'] = d.pop('cost_by_year')
    return d


def estimate_solar_home_electricity_internal_distribution_cost(**kw):
    d = OrderedDict()
    years = kw['population_by_year'].index
    d['electricity_internal_distribution_cost_by_year'] = Series(
        np.zeros(len(years)), index=years)
    return d


def estimate_solar_home_panel_cost(
        consumption_in_kwh_by_year,
        peak_hours_of_sun_per_year,
        solar_home_system_loss_as_percent_of_total_production,
        solar_home_panel_table):
    # Estimate desired capacity
    maximum_consumption_per_year_in_kwh = consumption_in_kwh_by_year.max()
    maximum_production_per_year_in_kwh = adjust_for_losses(
        maximum_consumption_per_year_in_kwh,
        solar_home_system_loss_as_percent_of_total_production / 100.)
    desired_system_capacity_in_kw = maximum_production_per_year_in_kwh / float(
        peak_hours_of_sun_per_year)
    # Choose panel type
    return prepare_actual_system_capacity(
        desired_system_capacity_in_kw,
        solar_home_panel_table, 'capacity_in_kw')


def estimate_solar_home_battery_cost(
        solar_home_panel_actual_system_capacity_in_kw,
        solar_home_battery_kwh_per_panel_kw,
        solar_home_battery_installation_lm_cost_per_battery_kwh,
        solar_home_battery_maintenance_lm_cost_per_kwh_per_year,
        solar_home_battery_lifetime_in_years):
    battery_storage_in_kwh = solar_home_panel_actual_system_capacity_in_kw * \
        solar_home_battery_kwh_per_panel_kw
    installation_lm_cost = battery_storage_in_kwh * \
        solar_home_battery_installation_lm_cost_per_battery_kwh
    d = OrderedDict()
    d['installation_lm_cost'] = installation_lm_cost
    d['maintenance_lm_cost_per_year'] = battery_storage_in_kwh * \
        solar_home_battery_maintenance_lm_cost_per_kwh_per_year
    d['replacement_lm_cost_per_year'] = installation_lm_cost / float(
        solar_home_battery_lifetime_in_years)
    return d


def estimate_solar_home_balance_cost(
        solar_home_panel_actual_system_capacity_in_kw,
        solar_home_balance_installation_lm_cost_per_panel_kw,
        solar_home_balance_maintenance_lm_cost_per_panel_kw_per_year,
        solar_home_balance_lifetime_in_years):
    installation_lm_cost = solar_home_panel_actual_system_capacity_in_kw * \
        solar_home_balance_installation_lm_cost_per_panel_kw
    d = OrderedDict()
    d['installation_lm_cost'] = installation_lm_cost
    d['maintenance_lm_cost_per_year'] = \
        solar_home_panel_actual_system_capacity_in_kw * \
        solar_home_balance_maintenance_lm_cost_per_panel_kw_per_year
    d['replacement_lm_cost_per_year'] = installation_lm_cost / float(
        solar_home_balance_lifetime_in_years)
    return d


def estimate_nodal_grid_mv_network_budget_in_meters(
        internal_discounted_cost_by_technology, **kw):
    standalone_cost = min(
        v for k, v in internal_discounted_cost_by_technology.items()
        if k != 'grid')
    mv_network_budget = \
        standalone_cost - internal_discounted_cost_by_technology['grid']
    d = prepare_component_cost_by_year([
        ('mv_line', estimate_grid_mv_line_cost_per_meter),
    ], kw, prefix='grid_')
    grid_mv_line_discounted_cost_per_meter = compute_discounted_cash_flow(
        d.pop('cost_by_year'),
        kw['financing_year'],
        kw['discount_rate_as_percent_of_cash_flow_per_year'])
    d['grid_mv_network_budget_in_meters'] = mv_network_budget / float(
        grid_mv_line_discounted_cost_per_meter)
    return d


def assemble_total_grid_mv_network(target_folder, infrastructure_graph):
    geocode = geopy.GoogleV3().geocode
    for node_id, node_attributes in infrastructure_graph.nodes_iter(data=True):
        lon = node_attributes.get('longitude')
        lat = node_attributes.get('latitude')
        if lon is None or lat is None:
            location = geocode(node_attributes['name'])
            lon, lat = location.longitude, location.latitude
        node_attributes.update(longitude=lon, latitude=lat)
    node_table = get_table_from_graph(infrastructure_graph, [
        'longitude', 'latitude', 'grid_mv_network_budget_in_meters'])
    node_table_path = join(target_folder, 'nodes-networker.csv')
    node_table.to_csv(node_table_path)
    nwk_settings = {
        'demand_nodes': {
            'filename': node_table_path,
            'x_column': 'longitude',
            'y_column': 'latitude',
            'budget_column': 'grid_mv_network_budget_in_meters',
        },
        'network_algorithm': 'mod_boruvka',
        'network_parameters': {
            'minimum_node_count': 2,
        }
    }
    nwk = NetworkerRunner(nwk_settings, target_folder)
    nwk.validate()
    msf = nwk.run()
    infrastructure_graph.add_edges_from(msf.edges_iter())
    return {'infrastructure_graph': infrastructure_graph}


def sequence_total_grid_mv_network(target_folder, infrastructure_graph):
    node_table = get_table_from_graph(infrastructure_graph, [
        'longitude', 'latitude', 'population', 'peak_demand_in_kw'])
    node_table = node_table.rename(columns={'longitude': 'X', 'latitude': 'Y'})
    node_table_path = join(target_folder, 'nodes-sequencer.csv')
    node_table.to_csv(node_table_path)
    edge_shapefile_path = join(target_folder, 'edges.shp')
    nwp = NetworkPlan(
        edge_shapefile_path, node_table_path, prioritize='population')
    model = EnergyMaximizeReturn(nwp)
    model.sequence()
    order_series = model.output_frame['Sequence..Far.sighted.sequence']
    for index, order in order_series.iteritems():
        infrastructure_graph.node[index]['order'] = order
    return {'infrastructure_graph': infrastructure_graph}


def estimate_total_cost(infrastructure_graph):
    print len(infrastructure_graph)
    return []


def grow_exponentially(value, growth_as_percent, growth_count):
    return value * (1 + growth_as_percent / 100.) ** growth_count


def prepare_internal_cost(fs, kw):
    d = OrderedDict()
    # Compute
    for f in fs:
        d.update(compute(f, kw))
    cost_by_year = sum([
        d['electricity_production_cost_by_year'],
        d['electricity_internal_distribution_cost_by_year'],
    ])
    financing_year = kw['financing_year']
    discount_rate = kw['discount_rate_as_percent_of_cash_flow_per_year']
    discounted_production_in_kwh = compute_discounted_cash_flow(
        d['electricity_production_in_kwh_by_year'],
        financing_year, discount_rate)
    discounted_cost = compute_discounted_cash_flow(
        cost_by_year, financing_year, discount_rate)
    levelized_cost = discounted_cost / float(discounted_production_in_kwh)
    # Summarize
    d['internal_discounted_cost'] = discounted_cost
    d['internal_levelized_cost'] = levelized_cost
    return d


def prepare_actual_system_capacity(
        desired_system_capacity, option_table, capacity_column_key):
    t = option_table
    capacity_column = C[capacity_column_key]
    # Select option
    eligible_t = t[t[capacity_column] < desired_system_capacity]
    if len(eligible_t):
        t = eligible_t
        # Choose the largest capacity from eligible types
        selected_t = t[t[capacity_column] == t[capacity_column].max()]
    else:
        # Choose the smallest capacity from all types
        selected_t = t[t[capacity_column] == t[capacity_column].min()]
    selected = selected_t.ix[selected_t.index[0]]
    # Get capacity and count
    selected_capacity = selected[capacity_column]
    selected_count = int(ceil(desired_system_capacity / float(
        selected_capacity)))
    actual_system_capacity = selected_capacity * selected_count
    # Get costs
    installation_lm_cost = selected_count * selected[C[
        'installation_lm_cost']]
    maintenance_lm_cost_per_year = selected_count * selected[C[
        'maintenance_lm_cost_per_year']]
    replacement_lm_cost_per_year = installation_lm_cost / float(selected[C[
        'lifetime_in_years']])
    return [
        ('desired_system_' + capacity_column_key, desired_system_capacity),
        ('selected_' + capacity_column_key, selected_capacity),
        ('selected_count', selected_count),
        ('actual_system_' + capacity_column_key, actual_system_capacity),
        ('installation_lm_cost', installation_lm_cost),
        ('maintenance_lm_cost_per_year', maintenance_lm_cost_per_year),
        ('replacement_lm_cost_per_year', replacement_lm_cost_per_year),
    ]


def prepare_component_cost_by_year(component_packs, kw, prefix):
    d = OrderedDict()
    cost_by_year_index = np.zeros(kw['time_horizon_in_years'] + 1)
    for component, estimate_component_cost in component_packs:
        v_by_k = OrderedDict(compute(estimate_component_cost, kw, d))
        # Add initial costs
        cost_by_year_index[0] += get_by_prefix(v_by_k, 'installation')
        # Add recurring costs
        cost_by_year_index[1:] += \
            get_by_prefix(v_by_k, 'maintenance') + \
            get_by_prefix(v_by_k, 'replacement')
        # Save
        d.update(rename_keys(v_by_k, prefix=prefix + component + '_'))
    years = kw['population_by_year'].index
    d['cost_by_year'] = Series(cost_by_year_index, index=years)
    return d


def prepare_lv_line_cost(
        connection_count_by_year,
        average_distance_between_buildings_in_meters,
        lv_line_installation_lm_cost_per_meter,
        lv_line_maintenance_lm_cost_per_meter_per_year,
        lv_line_lifetime_in_years):
    # TODO: Compute lv line cost by year as connections come online
    maximum_connection_count = connection_count_by_year.max()
    line_length_in_meters = average_distance_between_buildings_in_meters * (
        maximum_connection_count - 1)
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
        connection_count_by_year,
        lv_connection_installation_lm_cost_per_connection,
        lv_connection_maintenance_lm_cost_per_connection_per_year,
        lv_connection_lifetime_in_years):
    # TODO: Compute lv connection cost by year as connections come online
    maximum_connection_count = connection_count_by_year.max()
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
    'Discount cash flow starting from the year of financing'
    year_increments = np.array(cash_flow_by_year.index - financing_year)
    year_increments[year_increments < 0] = 0  # Do not discount prior years
    discount_rate_as_factor = 1 + discount_rate_as_percent / 100.
    return sum(cash_flow_by_year / discount_rate_as_factor ** year_increments)


def load_abbreviations(locale):
    return {
        'diesel_mini_grid_generator_minimum_hours_of_production_per_year': 'dmg_gen_mhoppy',  # noqa
    }


def load_column_names(locale):
    return {
        'name': 'name',
        'population': 'population',
        'year': 'year',
        'capacity_in_kva': 'capacity in kva',
        'capacity_in_kw': 'capacity in kw',
        'installation_lm_cost': 'installation labor and material cost',
        'maintenance_lm_cost_per_year': (
            'maintenance labor and material cost per year'),
        'lifetime_in_years': 'lifetime in years',
    }


def load_messages(locale):
    return {
        'bad_financing_year': (
            'financing year (%s) must be greater than or equal to '
            'population year (%s)'),
        'bad_power_factor': 'power factor (%s) must be between -1 and 1',
    }


A = load_abbreviations('en-US')
C = load_column_names('en-US')
M = load_messages('en-US')


TABLE_NAMES = [
    'demographic_table',
    'grid_mv_transformer_table',
    'diesel_mini_grid_generator_table',
    'solar_home_panel_table',
]
MAIN_FUNCTIONS = [
    estimate_nodal_population,
    estimate_nodal_consumption_in_kwh,
    estimate_nodal_peak_demand_in_kw,
    estimate_nodal_internal_cost_by_technology,
    estimate_nodal_grid_mv_network_budget_in_meters,
    assemble_total_grid_mv_network,
    sequence_total_grid_mv_network,
    estimate_total_cost,
]
COST_FUNCTION_BY_TECHNOLOGY = OrderedDict([
    ('grid', estimate_grid_internal_cost),
    ('diesel_mini_grid', estimate_diesel_mini_grid_internal_cost),
    ('solar_home', estimate_solar_home_internal_cost),
])


def run(target_folder, g):
    # Prepare
    for table_name in TABLE_NAMES:
        table = g[table_name]
        table.columns = normalize_column_names(table.columns, g['locale'])
    demographic_table = normalize_demographic_table(g['demographic_table'])
    g['target_folder'] = target_folder
    g['demographic_table'] = demographic_table
    g['infrastructure_graph'] = get_graph_from_table(demographic_table)
    # Compute
    for f in MAIN_FUNCTIONS:
        if '_total_' in f.func_name:
            try:
                g.update(compute(f, g))
            except InfrastructurePlanningError as e:
                exit('%s.error = %s : %s' % (e[0], f.func_name, e[1]))
            continue
        graph = g['infrastructure_graph']
        for node_id, node_attributes in graph.nodes_iter(data=True):
            # Perform node-level override
            node_defaults = dict(demographic_table.ix[node_id])
            l = merge_dictionaries(node_attributes, node_defaults)
            try:
                node_attributes.update(compute(f, l, g))
            except InfrastructurePlanningError as e:
                exit('%s.error = %s : %s : %s' % (
                    e[0], l['name'].encode('utf-8'), f.func_name, e[1]))

    ls = [x[1] for x in g['infrastructure_graph'].nodes_iter(data=True)]
    ls, g = sift_common_values(ls, g)
    # Save
    save_common_values(target_folder, g)
    save_unique_values(target_folder, ls)
    save_yearly_values(target_folder, ls)

    # Summarize
    keys = [
        'internal_discounted_cost_by_technology',
        'internal_levelized_cost_by_technology',
    ]
    d = OrderedDict()
    for key in keys:
        internal_cost_table = concat([Series(x[key]) for x in ls], axis=1)
        internal_cost_table.columns = [x['name'] for x in ls]
        internal_cost_table_path = join(target_folder, key + '.csv')
        internal_cost_table.transpose().to_csv(internal_cost_table_path)
        d[key + '_table_path'] = internal_cost_table_path

    # Map
    columns = ['Name', 'WKT', 'RadiusInPixelsRange10-50', 'Order']
    rows = []
    graph = g['infrastructure_graph']
    for node_id, node_attributes in graph.nodes_iter(data=True):
        name = node_attributes['name']
        longitude = node_attributes['longitude']
        latitude = node_attributes['latitude']
        population = node_attributes['population']
        order = node_attributes['order']
        wkt = Point(latitude, longitude).wkt
        rows.append([name, wkt, population, order])
    for node1_id, node2_id in graph.edges_iter():
        node1 = graph.node[node1_id]
        node2 = graph.node[node2_id]
        name = 'From %s to %s' % (node1['name'], node2['name'])
        wkt = LineString([
            (node1['latitude'], node1['longitude']),
            (node2['latitude'], node2['longitude']),
        ])
        rows.append([name, wkt, None, None])
    infrastructure_geotable_path = join(
        target_folder, 'infrastructure_streets_satellite.csv')
    infrastructure_geotable = DataFrame(rows, columns=columns)
    infrastructure_geotable.to_csv(infrastructure_geotable_path, index=False)
    print('infrastructure_geotable_path = %s' % infrastructure_geotable_path)

    return d


def normalize_column_names(columns, locale):
    'Translate each column name into English'
    return [x.lower() for x in columns]


def normalize_demographic_table(table):
    if 'year' in table.columns:
        table = table.rename(columns={'year': 'population_year'})
    if 'population_year' in table.columns:
        # Use most recent year
        table = table.sort('population_year').groupby('name').last()
        table = table.reset_index()
    return table


def get_graph_from_table(table):
    graph = Graph()
    for index, row in table.iterrows():
        graph.add_node(index, dict(row))
    return graph


def get_table_from_graph(graph, keys=None):
    index, rows = zip(*graph.nodes_iter(data=True))
    if keys:
        rows = ({k: d[k] for k in keys} for d in rows)
    return DataFrame(rows, index=index)


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


def sift_common_values(ls, g):
    'Move local arguments with common values into global arguments'
    ls, g = deepcopy(ls), copy(g)
    try:
        common_value_by_key = ls[0].copy()
    except IndexError:
        return ls, g
    for l in ls:
        for k, v in l.items():
            try:
                value = common_value_by_key[k]
            except KeyError:
                continue
            try:
                if v != value:
                    common_value_by_key.pop(k)
            except ValueError:
                if not v.equals(value):
                    common_value_by_key.pop(k)
    for key, value in common_value_by_key.items():
        g[key] = value
        for l in ls:
            l.pop(key)
    return ls, g


def rename_keys(value_by_key, prefix='', suffix=''):
    d = OrderedDict()
    for key, value in value_by_key.items():
        if prefix and not key.startswith(prefix):
            key = prefix + key
        if suffix and not key.endswith(suffix):
            key = key + suffix
        d[key] = value
    return d


def get_by_prefix(value_by_key, prefix):
    for key, value in value_by_key.items():
        if key.startswith(prefix):
            return value


def save_common_values(target_folder, g):
    target_path = join(target_folder, 'common_values.csv')
    # TODO: Clean this messiness
    # rows = [(A[k], v) for k, v in g.items()]
    rows = [
        (k, v) for k, v in g.items() if
        not k.endswith('_by_year') and
        not k.endswith('_table') and
        not k.endswith('_path') and
        not k.endswith('_folder') and
        not k.endswith('locale')]
    table = DataFrame(rows, columns=['Argument', 'Value'])
    table.to_csv(target_path, header=False, index=False)
    return target_path


def save_unique_values(target_folder, ls):
    target_path = join(target_folder, 'unique_values.csv')
    # TODO: Clean this messiness
    rows = [Series({
        k: v for k, v in l.items() if
        not k.endswith('_by_year') and
        not k.endswith('_by_technology') and
        k != 'name'
    }) for l in ls]
    table = concat(rows, axis=1)
    # table.columns = [A[k] for k in table.columns]
    table.columns = [l['name'] for l in ls]
    table.to_csv(target_path)
    table.transpose().to_csv(join(
        target_folder, 'unique_values_transposed.csv'), index=False)
    return target_path


def save_yearly_values(target_folder, ls):
    target_path = join(target_folder, 'yearly_values.csv')
    columns = OrderedDefaultDict(list)
    for l in ls:
        name = l['name']
        for k, v in l.items():
            if not k.endswith('_by_year') or v.empty:
                continue
            column = Series(v)
            # column.index = MultiIndex.from_tuples([(
            # name, x) for x in column.index], names=[A['name'], A['year']])
            column.index = MultiIndex.from_tuples([(
                name, x) for x in column.index], names=['name', 'year'])
            # columns[A[k.replace('_by_year', '')]].append(column)
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
        '--average_distance_between_buildings_in_meters',
        metavar='FLOAT', required=True, type=float)
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
        '--grid_electricity_production_cost_per_kwh',
        metavar='FLOAT', required=True, type=float)
    argument_parser.add_argument(
        '--grid_system_loss_as_percent_of_total_production',
        metavar='PERCENT', required=True, type=float)
    argument_parser.add_argument(
        '--grid_mv_transformer_load_power_factor',
        metavar='FLOAT', required=True, type=float)
    argument_parser.add_argument(
        '--grid_mv_transformer_table_path',
        metavar='PATH', required=True)

    argument_parser.add_argument(
        '--grid_mv_line_installation_lm_cost_per_meter',
        metavar='FLOAT', required=True, type=float)
    argument_parser.add_argument(
        '--grid_mv_line_maintenance_lm_cost_per_meter_per_year',
        metavar='FLOAT', required=True, type=float)
    argument_parser.add_argument(
        '--grid_mv_line_lifetime_in_years',
        metavar='FLOAT', required=True, type=float)

    argument_parser.add_argument(
        '--grid_lv_line_installation_lm_cost_per_meter',
        metavar='FLOAT', required=True, type=float)
    argument_parser.add_argument(
        '--grid_lv_line_maintenance_lm_cost_per_meter_per_year',
        metavar='FLOAT', required=True, type=float)
    argument_parser.add_argument(
        '--grid_lv_line_lifetime_in_years',
        metavar='FLOAT', required=True, type=float)

    argument_parser.add_argument(
        '--grid_lv_connection_installation_lm_cost_per_connection',
        metavar='FLOAT', required=True, type=float)
    argument_parser.add_argument(
        '--grid_lv_connection_maintenance_lm_cost_per_connection_per_year',
        metavar='FLOAT', required=True, type=float)
    argument_parser.add_argument(
        '--grid_lv_connection_lifetime_in_years',
        metavar='FLOAT', required=True, type=float)

    argument_parser.add_argument(
        '--diesel_mini_grid_system_loss_as_percent_of_total_production',
        metavar='PERCENT', required=True, type=float)
    argument_parser.add_argument(
        '--diesel_mini_grid_generator_table_path',
        metavar='PATH', required=True)
    argument_parser.add_argument(
        '--diesel_mini_grid_generator_minimum_hours_of_production_per_year',
        metavar='FLOAT', required=True, type=float)
    argument_parser.add_argument(
        '--diesel_mini_grid_fuel_cost_per_liter',
        metavar='FLOAT', required=True, type=float)
    argument_parser.add_argument(
        '--diesel_mini_grid_fuel_liters_consumed_per_kwh',
        metavar='FLOAT', required=True, type=float)

    argument_parser.add_argument(
        '--diesel_mini_grid_lv_line_installation_lm_cost_per_meter',
        metavar='FLOAT', required=True, type=float)
    argument_parser.add_argument(
        '--diesel_mini_grid_lv_line_maintenance_lm_cost_per_meter_per_year',
        metavar='FLOAT', required=True, type=float)
    argument_parser.add_argument(
        '--diesel_mini_grid_lv_line_lifetime_in_years',
        metavar='FLOAT', required=True, type=float)

    argument_parser.add_argument(
        '--diesel_mini_grid_lv_connection_installation_lm_cost_per_connection',
        metavar='FLOAT', required=True, type=float)
    argument_parser.add_argument(
        '--diesel_mini_grid_lv_connection_maintenance_lm_cost_per_connection_per_year',  # noqa
        metavar='FLOAT', required=True, type=float)
    argument_parser.add_argument(
        '--diesel_mini_grid_lv_connection_lifetime_in_years',
        metavar='FLOAT', required=True, type=float)

    argument_parser.add_argument(
        '--peak_hours_of_sun_per_year',
        metavar='FLOAT', required=True, type=float)
    argument_parser.add_argument(
        '--solar_home_system_loss_as_percent_of_total_production',
        metavar='PERCENT', required=True, type=float)
    argument_parser.add_argument(
        '--solar_home_panel_table_path',
        metavar='PATH', required=True)

    argument_parser.add_argument(
        '--solar_home_battery_kwh_per_panel_kw',
        metavar='FLOAT', required=True, type=float)
    argument_parser.add_argument(
        '--solar_home_battery_installation_lm_cost_per_battery_kwh',
        metavar='FLOAT', required=True, type=float)
    argument_parser.add_argument(
        '--solar_home_battery_maintenance_lm_cost_per_kwh_per_year',
        metavar='FLOAT', required=True, type=float)
    argument_parser.add_argument(
        '--solar_home_battery_lifetime_in_years',
        metavar='FLOAT', required=True, type=float)

    argument_parser.add_argument(
        '--solar_home_balance_installation_lm_cost_per_panel_kw',
        metavar='FLOAT', required=True, type=float)
    argument_parser.add_argument(
        '--solar_home_balance_maintenance_lm_cost_per_panel_kw_per_year',
        metavar='FLOAT', required=True, type=float)
    argument_parser.add_argument(
        '--solar_home_balance_lifetime_in_years',
        metavar='FLOAT', required=True, type=float)

    args = argument_parser.parse_args()
    A = load_abbreviations(args.locale)
    C = load_column_names(args.locale)
    M = load_messages(args.locale)
    g = args.__dict__.copy()
    g['demographic_table'] = read_csv(
        args.demographic_table_path)
    g['grid_mv_transformer_table'] = read_csv(
        args.grid_mv_transformer_table_path)
    g['diesel_mini_grid_generator_table'] = read_csv(
        args.diesel_mini_grid_generator_table_path)
    g['solar_home_panel_table'] = read_csv(
        args.solar_home_panel_table_path)
    d = run(args.target_folder or make_enumerated_folder_for(__file__), g)
    print(format_summary(d))
