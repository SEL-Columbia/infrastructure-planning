from ...finance.valuation import compute_discounted_cash_flow


def estimate_consumption_profile(
        connection_count_by_year, consumption_in_kwh_by_year, financing_year,
        discount_rate_as_percent_of_cash_flow_per_year):
    discounted_consumption_in_kwh = compute_discounted_cash_flow(
        consumption_in_kwh_by_year, financing_year,
        discount_rate_as_percent_of_cash_flow_per_year)
    return {
        'final_connection_count': connection_count_by_year.max(),
        'final_consumption_in_kwh_per_year': consumption_in_kwh_by_year.max(),
        'discounted_consumption_in_kwh': discounted_consumption_in_kwh,
    }
