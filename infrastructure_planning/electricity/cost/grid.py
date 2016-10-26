from collections import defaultdict
from geopy.distance import vincenty as get_distance
from invisibleroads_macros.math import divide_safely

from ...exceptions import ExpectedPositive, ValidationError
from ...finance.valuation import compute_discounted_cash_flow
from ...macros import get_final_value
from ...production import adjust_for_losses, prepare_system_cost
from .mini_grid import estimate_lv_connection_cost, estimate_lv_line_cost
from . import (
    prepare_component_cost_by_year, prepare_external_cost,
    prepare_internal_cost)


def estimate_internal_cost(**keywords):
    return prepare_internal_cost([
        estimate_electricity_production_cost,
        estimate_internal_distribution_cost,
    ], keywords)


def estimate_external_cost(**keywords):
    return prepare_external_cost([
        estimate_external_distribution_cost,
    ], keywords)


def estimate_external_distribution_cost(
        grid_mv_line_cost_per_meter_by_year, **keywords):
    return {
        'external_distribution_cost_by_year':
            keywords.get('grid_mv_line_adjusted_length_in_meters', 0) *
            grid_mv_line_cost_per_meter_by_year,
    }


def estimate_electricity_production_cost(
        consumption_in_kwh_by_year,
        grid_system_loss_as_percent_of_total_production,
        grid_mv_transformer_load_power_factor,
        grid_electricity_production_cost_per_kwh):
    if not -1 <= grid_mv_transformer_load_power_factor <= 1:
        raise ValidationError(
            'grid_mv_transformer_load_power_factor',
            'must be between -1 and +1')
    production_in_kwh_by_year = adjust_for_losses(
        consumption_in_kwh_by_year,
        grid_system_loss_as_percent_of_total_production,
        (1 - grid_mv_transformer_load_power_factor) * 100)
    return {
        'electricity_production_in_kwh_by_year': production_in_kwh_by_year,
        'electricity_production_cost_by_year':
            grid_electricity_production_cost_per_kwh *
            production_in_kwh_by_year,
    }


def estimate_internal_distribution_cost(**keywords):
    component_cost_by_year, d = prepare_component_cost_by_year([
        ('mv_transformer', estimate_grid_mv_transformer_cost),
        ('lv_line', estimate_grid_lv_line_cost),
        ('lv_connection', estimate_grid_lv_connection_cost),
    ], keywords, prefix='grid_')
    d['internal_distribution_cost_by_year'] = component_cost_by_year
    return d


def estimate_grid_mv_line_discounted_cost_per_meter(
        financing_year, discount_rate_as_percent_of_cash_flow_per_year,
        **keywords):
    component_cost_by_year, d = prepare_component_cost_by_year([
        ('mv_line', estimate_grid_mv_line_cost_per_meter),
    ], keywords, prefix='grid_')
    discounted_cost_per_meter = compute_discounted_cash_flow(
        component_cost_by_year, financing_year,
        discount_rate_as_percent_of_cash_flow_per_year)
    d['grid_mv_line_cost_per_meter_by_year'] = component_cost_by_year
    d['grid_mv_line_final_cost_per_meter_per_year'] = get_final_value(
        component_cost_by_year)
    d['grid_mv_line_discounted_cost_per_meter'] = discounted_cost_per_meter
    return d


def estimate_grid_mv_line_budget(
        internal_discounted_cost_by_technology,
        grid_mv_line_discounted_cost_per_meter, line_length_adjustment_factor):
    standalone_cost = min(
        v for k, v in internal_discounted_cost_by_technology.items()
        if k != 'grid')
    grid_mv_line_budget_in_money = \
        standalone_cost - internal_discounted_cost_by_technology['grid']
    grid_mv_line_raw_budget_in_meters = divide_safely(
        grid_mv_line_budget_in_money,
        grid_mv_line_discounted_cost_per_meter,
        ExpectedPositive('grid_mv_line_discounted_cost_per_meter'))
    # Divide line distance by factor here, which should be equivalent to
    # multiplying line distance by factor when computing the network
    grid_mv_line_adjusted_budget_in_meters = divide_safely(
        grid_mv_line_raw_budget_in_meters, line_length_adjustment_factor,
        ExpectedPositive('line_length_adjustment_factor'))
    return {
        'grid_mv_line_adjusted_budget_in_meters':
            grid_mv_line_adjusted_budget_in_meters,
    }


def estimate_grid_mv_line_adjusted_length_in_meters(
        node_id, latitude, longitude, line_length_adjustment_factor,
        infrastructure_graph, **keywords):
    d = defaultdict(float)
    key = 'grid_mv_line_adjusted_length_in_meters'
    relative_keys = [
        'grid_mv_line_raw_cost_per_meter',
        'grid_mv_line_installation_cost_per_meter',
        'grid_mv_line_maintenance_cost_per_meter_per_year',
        'grid_mv_line_replacement_cost_per_meter_per_year',
        'grid_mv_line_final_cost_per_meter_per_year',
        'grid_mv_line_discounted_cost_per_meter',
    ]
    # Note that node_id is real but edge_node_id can be fake
    for edge_node_id, edge_d in infrastructure_graph.edge[node_id].items():
        edge_node_d = infrastructure_graph.node[edge_node_id]
        edge_node_ll = edge_node_d['latitude'], edge_node_d['longitude']
        line_length = get_distance((latitude, longitude), edge_node_ll).meters
        if 'name' in edge_node_d:
            # If both nodes are real, then the computation will reappear when
            # we process the other node, so we halve it here
            line_length /= 2.
        line_adjusted_length = line_length * line_length_adjustment_factor
        # Aggregate over each node that is connected to the edge
        edge_d[key] = edge_d.get(key, 0) + line_adjusted_length
        d[key] += line_adjusted_length
        for relative_key in relative_keys:
            cost_per_meter = keywords[relative_key]
            x = cost_per_meter * line_adjusted_length
            k = relative_key.replace('_per_meter', '')
            edge_d[k] = edge_d.get(k, 0) + x
            d[k] += x
    return dict(d)


def estimate_grid_mv_line_cost_per_meter(
        grid_mv_line_raw_cost_per_meter,
        grid_mv_line_installation_cost_as_percent_of_raw_cost,
        grid_mv_line_maintenance_cost_per_year_as_percent_of_raw_cost,
        grid_mv_line_lifetime_in_years):
    raw_cost_per_meter = grid_mv_line_raw_cost_per_meter
    installation_cost_per_meter = raw_cost_per_meter * \
        grid_mv_line_installation_cost_as_percent_of_raw_cost / 100.
    return {
        'raw_cost_per_meter': raw_cost_per_meter,
        'installation_cost_per_meter': installation_cost_per_meter,
        'maintenance_cost_per_meter_per_year':
            raw_cost_per_meter *
            grid_mv_line_maintenance_cost_per_year_as_percent_of_raw_cost / 100.,  # noqa
        'replacement_cost_per_meter_per_year': divide_safely(
            raw_cost_per_meter + installation_cost_per_meter,
            grid_mv_line_lifetime_in_years,
            ExpectedPositive('grid_mv_line_lifetime_in_years')),
    }


def estimate_grid_mv_transformer_cost(
        peak_demand_in_kw,
        grid_system_loss_as_percent_of_total_production,
        grid_mv_transformer_load_power_factor,
        grid_mv_transformer_table):
    # Estimate desired capacity
    desired_system_capacity_in_kva = adjust_for_losses(
        peak_demand_in_kw,
        grid_system_loss_as_percent_of_total_production,
        (1 - grid_mv_transformer_load_power_factor) * 100)
    # Choose transformer type
    return prepare_system_cost(
        grid_mv_transformer_table, 'capacity_in_kva',
        desired_system_capacity_in_kva)


def estimate_grid_lv_line_cost(
        final_connection_count,
        line_length_adjustment_factor,
        average_distance_between_buildings_in_meters,
        grid_lv_line_raw_cost_per_meter,
        grid_lv_line_installation_cost_as_percent_of_raw_cost,
        grid_lv_line_maintenance_cost_per_year_as_percent_of_raw_cost,
        grid_lv_line_lifetime_in_years):
    return estimate_lv_line_cost(
        final_connection_count,
        line_length_adjustment_factor,
        average_distance_between_buildings_in_meters,
        grid_lv_line_raw_cost_per_meter,
        grid_lv_line_installation_cost_as_percent_of_raw_cost,
        grid_lv_line_maintenance_cost_per_year_as_percent_of_raw_cost,
        grid_lv_line_lifetime_in_years)


def estimate_grid_lv_connection_cost(
        final_connection_count,
        grid_lv_connection_raw_cost,
        grid_lv_connection_installation_cost_as_percent_of_raw_cost,
        grid_lv_connection_maintenance_cost_per_year_as_percent_of_raw_cost,
        grid_lv_connection_lifetime_in_years):
    return estimate_lv_connection_cost(
        final_connection_count,
        grid_lv_connection_raw_cost,
        grid_lv_connection_installation_cost_as_percent_of_raw_cost,
        grid_lv_connection_maintenance_cost_per_year_as_percent_of_raw_cost,
        grid_lv_connection_lifetime_in_years)
