

def estimate_lv_line_cost(
        final_connection_count,
        line_length_adjustment_factor,
        average_distance_between_buildings_in_meters,
        lv_line_installation_lm_cost_per_meter,
        lv_line_maintenance_lm_cost_per_meter_per_year,
        lv_line_lifetime_in_years):
    # TODO: Compute lv line cost by year as connections come online
    line_length_in_meters = average_distance_between_buildings_in_meters * (
        final_connection_count - 1) * line_length_adjustment_factor
    installation_lm_cost = line_length_in_meters * \
        lv_line_installation_lm_cost_per_meter
    maintenance_lm_cost_per_year = line_length_in_meters * \
        lv_line_maintenance_lm_cost_per_meter_per_year
    replacement_lm_cost_per_year = \
        installation_lm_cost / float(lv_line_lifetime_in_years)
    return {
        'installation_lm_cost': installation_lm_cost,
        'maintenance_lm_cost_per_year': maintenance_lm_cost_per_year,
        'replacement_lm_cost_per_year': replacement_lm_cost_per_year,
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
    replacement_lm_cost_per_year = \
        installation_lm_cost / float(lv_connection_lifetime_in_years)
    return {
        'installation_lm_cost': installation_lm_cost,
        'maintenance_lm_cost_per_year': maintenance_lm_cost_per_year,
        'replacement_lm_cost_per_year': replacement_lm_cost_per_year,
    }
