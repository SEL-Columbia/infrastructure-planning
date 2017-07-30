from invisibleroads_macros.calculator import divide_safely

from ..exceptions import ExpectedPositive


def estimate_peak_demand(
        final_consumption_in_kwh_per_year,
        consumption_during_peak_hours_as_percent_of_total_consumption,
        peak_hours_of_consumption_per_year):
    final_consumption_during_peak_hours_in_kwh_per_year = \
        final_consumption_in_kwh_per_year * \
        consumption_during_peak_hours_as_percent_of_total_consumption / 100.  # noqa
    # Choose to estimate peak demand by averaging kw over peak hours
    peak_demand_in_kw = divide_safely(
        final_consumption_during_peak_hours_in_kwh_per_year,
        peak_hours_of_consumption_per_year,
        ExpectedPositive('peak_hours_of_consumption_per_year'))
    return {
        'peak_demand_in_kw': peak_demand_in_kw,
    }
