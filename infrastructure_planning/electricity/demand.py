

def estimate_peak_demand(
        maximum_consumption_in_kwh_per_year,
        consumption_during_peak_hours_as_percent_of_total_consumption,
        peak_hours_of_consumption_per_year):
    maximum_consumption_during_peak_hours_in_kwh_per_year = \
        maximum_consumption_in_kwh_per_year * \
        consumption_during_peak_hours_as_percent_of_total_consumption / 100.
    peak_demand_in_kw = \
        maximum_consumption_during_peak_hours_in_kwh_per_year / float(
            peak_hours_of_consumption_per_year)
    return [
        ('peak_demand_in_kw', peak_demand_in_kw),
    ]
