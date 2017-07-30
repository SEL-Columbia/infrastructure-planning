from invisibleroads_macros.calculator import divide_safely
from pandas import DataFrame, Series, concat, isnull, merge

from ...growth import get_default_slope, get_future_years
from ...growth.interpolated import (
    get_interpolated_spline_extrapolated_linear_function as
    get_estimate_electricity_consumption)
from ...macros import get_final_value, make_zero_by_year


def estimate_consumption_from_connection_type(
        population_by_year, number_of_people_per_household,
        connection_type_table, **keywords):
    """
    Note that connection_count and consumption will be constant year over year
    if there is a local override for household_count.
    """
    d = {}
    connection_count_by_year = make_zero_by_year(population_by_year)
    consumption_by_year = make_zero_by_year(population_by_year)
    estimated_household_connection_count_by_year = divide_safely(
        population_by_year, number_of_people_per_household,
        make_zero_by_year(population_by_year))
    for row_index, row in connection_type_table.iterrows():
        connection_type = row['connection_type']
        count_by_year = _get_connection_count_by_year(
            keywords, connection_type,
            estimated_household_connection_count_by_year)
        consumption_per_connection = _get_consumption_per_connection(
            keywords, connection_type, row['consumption_in_kwh_per_year'])
        connection_count_by_year += count_by_year
        consumption_by_year += consumption_per_connection * count_by_year
        # Record
        connection_count_name = _name_connection_count(connection_type)
        consumption_per_connection_name = _name_consumption_per_connection(
            connection_type)
        d[connection_count_name + '_by_year'] = count_by_year
        d[connection_count_name] = get_final_value(count_by_year)
        d[consumption_per_connection_name] = consumption_per_connection
    return dict(d, **{
        'connection_count_by_year': connection_count_by_year,
        'consumption_in_kwh_by_year': consumption_by_year})


def estimate_consumption_from_connection_count(
        population_by_year,
        number_of_people_per_connection,
        consumption_in_kwh_per_year_per_connection):
    connection_count_by_year = divide_safely(
        population_by_year, number_of_people_per_connection, 0)
    consumption_by_year = consumption_in_kwh_per_year_per_connection * \
        connection_count_by_year
    return {
        'connection_count_by_year': connection_count_by_year,
        'consumption_in_kwh_by_year': consumption_by_year}


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


def _get_connection_count_by_year(
        keywords, connection_type,
        estimated_household_connection_count_by_year):
    year_index = estimated_household_connection_count_by_year.index
    column_name = _name_connection_count(connection_type)
    try:
        connection_count = keywords[column_name]
        if isnull(connection_count):
            raise KeyError
    except KeyError:
        if connection_type == 'household':
            return estimated_household_connection_count_by_year
        connection_count = 0
    return Series(connection_count, index=year_index)


def _get_consumption_per_connection(
        keywords, connection_type, estimated_consumption_per_connection):
    column_name = _name_consumption_per_connection(connection_type)
    try:
        # Enable local override
        consumption_per_connection = keywords[column_name]
        if isnull(consumption_per_connection):
            raise KeyError
    except KeyError:
        consumption_per_connection = estimated_consumption_per_connection
    return consumption_per_connection


def _name_connection_count(connection_type):
    return 'X_connection_count'.replace('X', connection_type)


def _name_consumption_per_connection(connection_type):
    return 'X_consumption_in_kwh_per_year_per_X'.replace('X', connection_type)
