from pandas import DataFrame, concat, merge

from ...growth import get_future_years, get_linear_model, prepare_xs


def estimate_electricity_consumption_from_series(
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
        forecast_electricity_consumption_per_capita_from_series(
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


def forecast_electricity_consumption_per_capita_from_series(
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
    ]].values

    growth_model = get_linear_model(
        year_packs, default_yearly_electricity_consumption_growth_percent)

    years = get_future_years(target_year, year_packs)
    if not years:
        return electricity_consumption_per_capita_by_year_table
    values = growth_model.predict(prepare_xs(years))

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
