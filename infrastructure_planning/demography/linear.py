import numpy as np
from collections import defaultdict
from pandas import DataFrame, concat

from ..growth import get_future_years, get_linear_model, prepare_xs


make_whole_number = lambda x: int(x) if x > 0 else 0


def forecast_demographic_from_series(
        target_year,
        demographic_by_year_table,
        demographic_by_year_table_name_column,
        demographic_by_year_table_year_column,
        demographic_by_year_table_population_column,
        default_yearly_population_growth_percent):

    demographic_by_year_table[[
        demographic_by_year_table_year_column,
        demographic_by_year_table_population_column,
    ]] = demographic_by_year_table[[
        demographic_by_year_table_year_column,
        demographic_by_year_table_population_column,
    ]].astype(int)

    name_packs = _get_name_packs(
        demographic_by_year_table,
        demographic_by_year_table_name_column,
        demographic_by_year_table_year_column,
        demographic_by_year_table_population_column)

    growth_models = [get_linear_model(
        year_packs, default_yearly_population_growth_percent,
    ) for name, year_packs in name_packs]

    name_packs = _estimate_future_population_counts(
        target_year, name_packs, growth_models)

    return concat([demographic_by_year_table, _get_demographic_by_year_table(
        name_packs,
        demographic_by_year_table_name_column,
        demographic_by_year_table_year_column,
        demographic_by_year_table_population_column),
    ])[demographic_by_year_table.columns].sort([
        demographic_by_year_table_name_column,
        demographic_by_year_table_year_column])


def _get_name_packs(
        demographic_by_year_table,
        name_column, year_column, population_column):
    year_packs_by_name = defaultdict(list)
    for index, row in demographic_by_year_table.sort(year_column).iterrows():
        name = row[name_column]
        year = row[year_column]
        population = make_whole_number(row[population_column])
        year_packs_by_name[name].append((year, population))
    return dict(year_packs_by_name).items()


def _estimate_future_population_counts(
        target_year, name_packs, growth_models):
    extended_name_packs = []
    make_whole_numbers = np.vectorize(make_whole_number)
    for (name, year_packs), growth_model in zip(name_packs, growth_models):
        years = get_future_years(target_year, year_packs)
        if not years:
            continue
        populations = make_whole_numbers(
            growth_model.predict(prepare_xs(years)))
        extended_name_packs.append((name, zip(years, populations)))
    return extended_name_packs


def _get_demographic_by_year_table(
        name_packs, name_column, year_column, population_column):
    rows = []
    for name, year_packs in name_packs:
        for year, population in year_packs:
            rows.append([name, year, population])
    return DataFrame(rows, columns=[
        name_column, year_column, population_column])
