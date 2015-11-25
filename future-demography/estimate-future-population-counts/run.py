import numpy as np
from argparse import ArgumentParser
from collections import defaultdict
from crosscompute_table import TableType
from invisibleroads_macros.disk import make_enumerated_folder_for, make_folder
from invisibleroads_macros.log import format_summary
from math import ceil
from os.path import join
from pandas import DataFrame, concat
from sklearn.linear_model import LinearRegression


prepare_data = lambda x: np.array(x).reshape((len(x), 1))


def run(
        target_folder, target_year, population_table,
        name_column, population_column, year_column, yearly_growth_percent):
    name_packs = get_name_packs(
        population_table, name_column, year_column, population_column)
    growth_models = get_growth_models(name_packs, yearly_growth_percent)
    name_packs = estimate_future_population_counts(
        target_year, name_packs, growth_models)
    population_table = concat([population_table, get_population_table(
        name_packs, name_column, year_column, population_column),
    ])[population_table.columns].sort_values([name_column, year_column])
    population_table_path = join(target_folder, 'populations.csv')
    population_table.to_csv(population_table_path, index=False)
    return {
        'population_table_path': population_table_path,
    }


def get_name_packs(
        population_table, name_column, year_column, population_column):
    year_packs_by_name = defaultdict(list)
    for index, row in population_table.sort_values(year_column).iterrows():
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
    for (name, old_year_packs), growth_model in zip(name_packs, growth_models):
        year, population = sorted(old_year_packs)[-1]
        years = range(year + 1, target_year + 1)
        populations = make_whole_numbers(
            growth_model.predict(prepare_data(years)))
        extended_name_packs.append((name, zip(years, populations)))
    return extended_name_packs


def get_population_table(
        name_packs, name_column, year_column, population_column):
    rows = []
    for name, year_packs in name_packs:
        for year, population in year_packs:
            rows.append([name, year, population])
    return DataFrame(rows, columns=[
        name_column, year_column, population_column])


if __name__ == '__main__':
    argument_parser = ArgumentParser()
    argument_parser.add_argument(
        '--target_folder', metavar='FOLDER', type=make_folder)
    argument_parser.add_argument(
        '--target_year', metavar='YEAR', type=int,
        required=True)
    argument_parser.add_argument(
        '--population_table_path', metavar='PATH',
        required=True)
    argument_parser.add_argument(
        '--name_column', metavar='COLUMN',
        required=True)
    argument_parser.add_argument(
        '--year_column', metavar='COLUMN',
        required=True)
    argument_parser.add_argument(
        '--population_column', metavar='COLUMN',
        required=True)
    argument_parser.add_argument(
        '--yearly_growth_percent', metavar='PERCENT', type=float,
        required=True)
    args = argument_parser.parse_args()
    d = run(
        args.target_folder or make_enumerated_folder_for(__file__),
        args.target_year,
        TableType().load(args.population_table_path),
        args.name_column,
        args.population_column,
        args.year_column,
        args.yearly_growth_percent)
    print(format_summary(d))
