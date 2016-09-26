from invisibleroads_macros.math import divide_safely

from ...exceptions import ExpectedPositive


def estimate_lv_line_cost(
        final_connection_count,
        line_length_adjustment_factor,
        average_distance_between_buildings_in_meters,
        lv_line_raw_cost_per_meter,
        lv_line_installation_cost_as_percent_of_raw_cost,
        lv_line_maintenance_cost_per_year_as_percent_of_raw_cost,
        lv_line_lifetime_in_years):
    # TODO: Compute lv line cost by year as connections come online
    line_length_in_meters = average_distance_between_buildings_in_meters * (
        final_connection_count - 1) * line_length_adjustment_factor
    raw_cost = line_length_in_meters * \
        lv_line_raw_cost_per_meter
    installation_cost = raw_cost * \
        lv_line_installation_cost_as_percent_of_raw_cost / float(100)
    maintenance_cost_per_year = raw_cost * \
        lv_line_maintenance_cost_per_year_as_percent_of_raw_cost / float(100)
    replacement_cost_per_year = divide_safely(
        raw_cost, lv_line_lifetime_in_years,
        ExpectedPositive('lv_line_lifetime_in_years'))
    return {
        'raw_cost': raw_cost,
        'installation_cost': installation_cost,
        'maintenance_cost_per_year': maintenance_cost_per_year,
        'replacement_cost_per_year': replacement_cost_per_year,
    }


def estimate_lv_connection_cost(
        final_connection_count,
        lv_connection_installation_lm_cost_per_connection,
        lv_connection_maintenance_lm_cost_per_connection_per_year,
        lv_connection_lifetime_in_years):
    # TODO: Compute lv connection cost by year as connections come online
    installation_lm_cost = final_connection_count * \
        lv_connection_installation_lm_cost_per_connection
    maintenance_lm_cost_per_year = final_connection_count * \
        lv_connection_maintenance_lm_cost_per_connection_per_year
    replacement_lm_cost_per_year = divide_safely(
        installation_lm_cost, lv_connection_lifetime_in_years,
        ExpectedPositive('lv_connection_lifetime_in_years'))
    return {
        'installation_lm_cost': installation_lm_cost,
        'maintenance_lm_cost_per_year': maintenance_lm_cost_per_year,
        'replacement_lm_cost_per_year': replacement_lm_cost_per_year,
    }
