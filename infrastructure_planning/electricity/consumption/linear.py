from infrastructure_planning.demography.linear import forecast_demographic


def forecast_electricity_consumption(
        target_folder, demographic_table,
        name_column, population_column, year_column,
        target_year, yearly_population_growth_percent,
        electricity_consumption_per_capita_table):

    # get future population
    # get future consumption in kWh per capita
    # multiply the two to get future consumption
    # save the consumption table,
    # adding another column that is called electricity consumption in kWh
    electricity_consumption_table_path = ''

    return [(
        'electricity_consumption_table_path',
        electricity_consumption_table_path,
    )]
