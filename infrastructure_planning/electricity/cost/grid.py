from geopy.distance import vincenty as get_distance
from invisibleroads_macros.math import divide_safely

from ...exceptions import ExpectedPositive, InfrastructurePlanningError
from ...finance.valuation import compute_discounted_cash_flow
from ...production import adjust_for_losses, prepare_system_cost
from .mini_grid import estimate_lv_connection_cost, estimate_lv_line_cost
from . import prepare_component_cost_by_year, prepare_internal_cost


def estimate_internal_cost(**keywords):
    return prepare_internal_cost([
        estimate_electricity_production_cost,
        estimate_electricity_internal_distribution_cost,
    ], keywords)


def estimate_external_cost(
        node_id, latitude, longitude, infrastructure_graph,
        line_length_adjustment_factor, grid_mv_line_discounted_cost_per_meter):
    node_line_discounted_cost = 0
    node_line_adjusted_length = 0
    node_ll = latitude, longitude
    # We can be sure that node_id is not a fake node
    # However, edge_node_id can be a fake node
    for edge_node_id, edge_d in infrastructure_graph.edge[node_id].items():
        edge_node_d = infrastructure_graph.node[edge_node_id]
        edge_node_ll = edge_node_d['latitude'], edge_node_d['longitude']
        edge_line_length = get_distance(node_ll, edge_node_ll).meters
        if 'name' in edge_node_d:
            # If both nodes are real, then the computation will reappear when
            # we process the other node, so we will halve it here.
            edge_line_length /= 2.
        edge_line_adjusted_length = edge_line_length * \
            line_length_adjustment_factor
        edge_line_discounted_cost = edge_line_adjusted_length * \
            grid_mv_line_discounted_cost_per_meter
        node_line_adjusted_length += edge_line_adjusted_length
        node_line_discounted_cost += edge_line_discounted_cost
        # Aggregate values over each node that is connected to the edge
        edge_d['grid_mv_line_adjusted_length_in_meters'] = \
            edge_d.get('grid_mv_line_adjusted_length_in_meters', 0) + \
            edge_line_adjusted_length
        edge_d['grid_mv_line_discounted_cost'] = \
            edge_d.get('grid_mv_line_discounted_cost', 0) + \
            edge_line_discounted_cost
    return {
        'mv_line_adjusted_length_in_meters': node_line_adjusted_length,
        'external_discounted_cost': node_line_discounted_cost,
    }


def estimate_electricity_production_cost(
        consumption_in_kwh_by_year,
        grid_system_loss_as_percent_of_total_production,
        grid_mv_transformer_load_power_factor,
        grid_electricity_production_cost_per_kwh):
    if not -1 <= grid_mv_transformer_load_power_factor <= 1:
        raise InfrastructurePlanningError(
            'grid_mv_transformer_load_power_factor', (
                'power factor (%s) must be between '
                '-1 and 1' % grid_mv_transformer_load_power_factor))
    production_in_kwh_by_year = adjust_for_losses(
        consumption_in_kwh_by_year,
        grid_system_loss_as_percent_of_total_production / 100.,
        1 - grid_mv_transformer_load_power_factor)
    d = {}
    d['electricity_production_in_kwh_by_year'] = production_in_kwh_by_year
    d['electricity_production_cost_by_year'] = \
        grid_electricity_production_cost_per_kwh * production_in_kwh_by_year
    return d


def estimate_electricity_internal_distribution_cost(**keywords):
    d = prepare_component_cost_by_year([
        ('mv_transformer', estimate_grid_mv_transformer_cost),
        ('lv_line', estimate_grid_lv_line_cost),
        ('lv_connection', estimate_grid_lv_connection_cost),
    ], keywords, prefix='grid_')
    d['electricity_internal_distribution_cost_by_year'] = d.pop('cost_by_year')
    return d


def estimate_grid_mv_line_budget(
        internal_discounted_cost_by_technology, line_length_adjustment_factor,
        financing_year, discount_rate_as_percent_of_cash_flow_per_year,
        **keywords):
    standalone_cost = min(
        v for k, v in internal_discounted_cost_by_technology.items()
        if k != 'grid')
    grid_mv_line_budget_in_money = \
        standalone_cost - internal_discounted_cost_by_technology['grid']
    d = prepare_component_cost_by_year([
        ('mv_line', estimate_grid_mv_line_cost_per_meter),
    ], keywords, prefix='grid_')
    grid_mv_line_discounted_cost_per_meter = compute_discounted_cash_flow(
        d.pop('cost_by_year'), financing_year,
        discount_rate_as_percent_of_cash_flow_per_year)
    grid_mv_line_raw_budget_in_meters = divide_safely(
        grid_mv_line_budget_in_money,
        grid_mv_line_discounted_cost_per_meter,
        ExpectedPositive('grid_mv_line_discounted_cost_per_meter'))
    d['grid_mv_line_discounted_cost_per_meter'] = \
        grid_mv_line_discounted_cost_per_meter
    # TODO: Update networker to accept line_length_adjustment_factor
    # Divide line distance by factor here, which should be equivalent to
    # multiplying line distance by factor when computing the network
    d['grid_mv_line_adjusted_budget_in_meters'] = divide_safely(
        grid_mv_line_raw_budget_in_meters,
        line_length_adjustment_factor,
        ExpectedPositive('line_length_adjustment_factor'))
    return d


def estimate_grid_mv_line_cost_per_meter(
        grid_mv_line_raw_cost_per_meter,
        grid_mv_line_installation_cost_as_percent_of_raw_cost,
        grid_mv_line_maintenance_cost_per_year_as_percent_of_raw_cost,
        grid_mv_line_lifetime_in_years):
    raw_cost_per_meter = grid_mv_line_raw_cost_per_meter
    installation_cost_per_meter = raw_cost_per_meter * \
        grid_mv_line_installation_cost_as_percent_of_raw_cost
    return {
        'raw_cost_per_meter': raw_cost_per_meter,
        'installation_cost_per_meter': installation_cost_per_meter,
        'maintenance_cost_per_meter_per_year': raw_cost_per_meter * \
            grid_mv_line_maintenance_cost_per_year_as_percent_of_raw_cost,
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
        grid_system_loss_as_percent_of_total_production / 100.,
        1 - grid_mv_transformer_load_power_factor)
    # Choose transformer type
    return prepare_system_cost(
        desired_system_capacity_in_kva,
        grid_mv_transformer_table, 'capacity_in_kva')


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
