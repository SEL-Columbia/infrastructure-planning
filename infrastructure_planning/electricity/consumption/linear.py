from pandas import DataFrame, concat, merge

from ...demography.linear import forecast_demographic
from ...growth import get_future_years, get_linear_model, prepare_xs


def forecast_electricity_consumption_from_demographic(
        target_year,
        demographic_table,
        demographic_name_column,
        demographic_population_column,
        demographic_year_column,
        default_yearly_population_growth_percent,
        electricity_consumption_per_capita_table,
        electricity_consumption_per_capita_year_column,
        electricity_consumption_per_capita_consumption_per_capita_column,
        default_yearly_electricity_consumption_growth_percent):

    demographic_table = forecast_demographic(
        target_year,
        demographic_table,
        demographic_name_column,
        demographic_population_column,
        demographic_year_column,
        default_yearly_population_growth_percent)

    electricity_consumption_per_capita_table = \
        forecast_electricity_consumption_per_capita(
            target_year,
            electricity_consumption_per_capita_table,
            electricity_consumption_per_capita_year_column,
            electricity_consumption_per_capita_consumption_per_capita_column,
            default_yearly_electricity_consumption_growth_percent)

    electricity_consumption_table = merge(
        demographic_table,
        electricity_consumption_per_capita_table,
        left_on=demographic_year_column,
        right_on=electricity_consumption_per_capita_year_column)

    electricity_consumption_table['Electricity Consumption'] = \
        electricity_consumption_table[
            electricity_consumption_per_capita_consumption_per_capita_column
        ] * electricity_consumption_table[demographic_population_column]

    return electricity_consumption_table.sort_values([
        demographic_name_column,
        demographic_year_column])


def forecast_electricity_consumption_per_capita(
        target_year,
        electricity_consumption_per_capita_table,
        electricity_consumption_per_capita_year_column,
        electricity_consumption_per_capita_consumption_per_capita_column,
        default_yearly_electricity_consumption_growth_percent):

    electricity_consumption_per_capita_table[
        electricity_consumption_per_capita_year_column
    ] = electricity_consumption_per_capita_table[
        electricity_consumption_per_capita_year_column
    ].astype(int)

    year_packs = electricity_consumption_per_capita_table[[
        electricity_consumption_per_capita_year_column,
        electricity_consumption_per_capita_consumption_per_capita_column,
    ]].values

    growth_model = get_linear_model(
        year_packs, default_yearly_electricity_consumption_growth_percent)

    years = get_future_years(target_year, year_packs)
    if not years:
        return electricity_consumption_per_capita_table
    values = growth_model.predict(prepare_xs(years))

    return concat([
        electricity_consumption_per_capita_table,
        DataFrame(zip(years, values), columns=[
            electricity_consumption_per_capita_year_column,
            electricity_consumption_per_capita_consumption_per_capita_column])
    ])[[
        electricity_consumption_per_capita_year_column,
        electricity_consumption_per_capita_consumption_per_capita_column,
    ]].sort_values([
        electricity_consumption_per_capita_year_column,
    ])
