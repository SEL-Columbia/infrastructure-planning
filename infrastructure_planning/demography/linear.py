import numpy as np
from collections import defaultdict
from math import ceil
from os.path import join
from pandas import DataFrame, concat
from sklearn.linear_model import LinearRegression


prepare_data = lambda x: np.array(x).reshape((len(x), 1))


def forecast_demographic(
        target_folder, demographic_table,
        name_column, population_column, year_column,
        target_year, yearly_population_growth_percent):
    name_packs = get_name_packs(
        demographic_table, name_column, year_column, population_column)
    growth_models = get_growth_models(
        name_packs, yearly_population_growth_percent)
    name_packs = estimate_future_population_counts(
        target_year, name_packs, growth_models)
    demographic_table = concat([demographic_table, get_demographic_table(
        name_packs, name_column, year_column, population_column),
    ])[demographic_table.columns].sort_values([name_column, year_column])
    demographic_table_path = join(target_folder, 'demographic.csv')
    demographic_table.to_csv(demographic_table_path, index=False)
    return [
        ('demographic_table_path', demographic_table_path),
    ]


def get_name_packs(
        demographic_table, name_column, year_column, population_column):
    year_packs_by_name = defaultdict(list)
    for index, row in demographic_table.sort_values(year_column).iterrows():
        name = row[name_column]
        year = row[year_column]
        population = row[population_column]
        year_packs_by_name[name].append((year, population))
    return dict(year_packs_by_name).items()


def get_growth_models(name_packs, yearly_growth_percent):
    growth_models = []
    yearly_growth_factor = 1 + yearly_growth_percent / 100.
    for name, year_packs in name_packs:
        growth_model = LinearRegression()
        if len(year_packs) == 1:
            year, population = year_packs[-1]
            years = [year, year + 1]
            populations = [population, population * yearly_growth_factor]
        else:
            year_array = np.array(year_packs)
            years = year_array[:, 0]
            populations = year_array[:, 1]
        growth_model.fit(prepare_data(years), populations)
        growth_models.append(growth_model)
    return growth_models


def estimate_future_population_counts(
        target_year, name_packs, growth_models):
    extended_name_packs = []
    make_whole_numbers = np.vectorize(lambda x: int(ceil(x)) if x > 0 else 0)
    for (name, year_packs), growth_model in zip(name_packs, growth_models):
        years = get_future_years(target_year, year_packs)
        if not years:
            continue
        populations = make_whole_numbers(
            growth_model.predict(prepare_data(years)))
        extended_name_packs.append((name, zip(years, populations)))
    return extended_name_packs


def get_demographic_table(
        name_packs, name_column, year_column, population_column):
    rows = []
    for name, year_packs in name_packs:
        for year, population in year_packs:
            rows.append([name, year, population])
    return DataFrame(rows, columns=[
        name_column, year_column, population_column])


def get_future_years(target_year, year_packs):
    past_years = sorted(x[0] for x in year_packs)
    future_years = range(past_years[-1] + 1, target_year)
    if target_year not in past_years:
        future_years.append(target_year)
    return future_years
