from pandas import DataFrame, concat, merge

from ...growth import get_default_slope, get_future_years
from ...growth.interpolated import get_interpolated_spline_extrapolated_linear_function as get_estimate_electricity_consumption  # noqa


def estimate_consumption(
        population_by_year,
        number_of_people_per_connection,
        consumption_in_kwh_per_connection):
    t = DataFrame({'population': population_by_year})
    t['connection_count'] = t['population'] / float(
        number_of_people_per_connection)
    t['consumption'] = consumption_in_kwh_per_connection * t[
        'connection_count']
    return {
        'connection_count_by_year': t['connection_count'],
        'consumption_in_kwh_by_year': t['consumption'],
        'maximum_connection_count': t['connection_count'].max(),
        'maximum_consumption_in_kwh_per_year': t['consumption'].max(),
    }


def estimate_electricity_consumption_using_recent_records(
        demographic_by_year_table,
        demographic_by_year_table_name_column,
        demographic_by_year_table_year_column,
        demographic_by_year_table_population_column,
        electricity_consumption_per_capita_by_year_table,
        electricity_consumption_per_capita_by_year_table_year_column,
        electricity_consumption_per_capita_by_year_table_consumption_per_capita_column,  # noqa
        default_yearly_electricity_consumption_growth_percent):

    target_year = demographic_by_year_table[
        demographic_by_year_table_year_column].max()

    electricity_consumption_per_capita_table = \
        forecast_electricity_consumption_per_capita_using_recent_records(
            target_year,
            electricity_consumption_per_capita_by_year_table,
            electricity_consumption_per_capita_by_year_table_year_column,
            electricity_consumption_per_capita_by_year_table_consumption_per_capita_column,  # noqa
            default_yearly_electricity_consumption_growth_percent)

    electricity_consumption_table = merge(
        demographic_by_year_table,
        electricity_consumption_per_capita_table,
        left_on=demographic_by_year_table_year_column,
        right_on=electricity_consumption_per_capita_by_year_table_year_column)

    electricity_consumption_table['Electricity Consumption'] = \
        electricity_consumption_table[
            electricity_consumption_per_capita_by_year_table_consumption_per_capita_column  # noqa
        ] * electricity_consumption_table[demographic_by_year_table_population_column]  # noqa

    return electricity_consumption_table.sort([
        demographic_by_year_table_name_column,
        demographic_by_year_table_year_column])


def forecast_electricity_consumption_per_capita_using_recent_records(
        target_year,
        electricity_consumption_per_capita_by_year_table,
        electricity_consumption_per_capita_by_year_table_year_column,
        electricity_consumption_per_capita_by_year_table_consumption_per_capita_column,  # noqa
        default_yearly_electricity_consumption_growth_percent):

    electricity_consumption_per_capita_by_year_table[
        electricity_consumption_per_capita_by_year_table_year_column
    ] = electricity_consumption_per_capita_by_year_table[
        electricity_consumption_per_capita_by_year_table_year_column
    ].astype(int)

    year_packs = electricity_consumption_per_capita_by_year_table[[
        electricity_consumption_per_capita_by_year_table_year_column,
        electricity_consumption_per_capita_by_year_table_consumption_per_capita_column,  # noqa
    ]].values.tolist()

    estimate_electricity_consumption = get_estimate_electricity_consumption(
        year_packs, get_default_slope(
            default_yearly_electricity_consumption_growth_percent, year_packs))

    years = get_future_years(target_year, year_packs)
    if not years:
        return electricity_consumption_per_capita_by_year_table
    values = estimate_electricity_consumption(years)

    return concat([
        electricity_consumption_per_capita_by_year_table,
        DataFrame(zip(years, values), columns=[
            electricity_consumption_per_capita_by_year_table_year_column,
            electricity_consumption_per_capita_by_year_table_consumption_per_capita_column])  # noqa
    ])[[
        electricity_consumption_per_capita_by_year_table_year_column,
        electricity_consumption_per_capita_by_year_table_consumption_per_capita_column,  # noqa
    ]].sort([
        electricity_consumption_per_capita_by_year_table_year_column,
    ])
