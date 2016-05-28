

def estimate_peak_demand(
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
