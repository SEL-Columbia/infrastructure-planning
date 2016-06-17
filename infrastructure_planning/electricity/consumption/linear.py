from pandas import DataFrame, Series, concat, merge

from ...growth import get_default_slope, get_future_years
from ...growth.interpolated import get_interpolated_spline_extrapolated_linear_function as get_estimate_electricity_consumption  # noqa


def estimate_consumption_from_connection_type(
        population_by_year,
        number_of_people_per_household,
        connection_type_table, **keywords):
    """
    Note that connection_count and consumption will be constant year over year
    if there is a local override for household_count.
    """
    connection_count_by_year = Series(0, index=population_by_year.index)
    consumption_by_year = Series(0, index=population_by_year.index)
    for row_index, row in connection_type_table.iterrows():
	connection_type = row['connection_type']
	try:
	    connection_count = keywords[connection_type + '_count']
	except KeyError:
	    if connection_type != 'household':
		continue
            # Estimate household_count from population
	    connection_count = population_by_year / float(number_of_people_per_household)
	consumption_per_connection = row['consumption_in_kwh_per_year']
	consumption_by_year += consumption_per_connection * connection_count
	connection_count_by_year += connection_count
    return {
        'connection_count_by_year': connection_count_by_year,
        'consumption_in_kwh_by_year': consumption_by_year,
        'maximum_connection_count': connection_count_by_year.max(),
        'maximum_consumption_in_kwh_per_year': consumption_by_year.max(),
    }


def estimate_consumption_from_connection_count(
        population_by_year,
        number_of_people_per_connection,
        consumption_in_kwh_per_year_per_connection):
    connection_count_by_year = population_by_year / float(
        number_of_people_per_connection)
    consumption_by_year = consumption_in_kwh_per_year_per_connection * \
        connection_count_by_year
    return {
        'connection_count_by_year': connection_count_by_year,
        'consumption_in_kwh_by_year': consumption_by_year ,
        'maximum_connection_count': connection_count_by_year.max(),
        'maximum_consumption_in_kwh_per_year': consumption_by_year.max(),
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
