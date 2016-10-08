from pandas import DataFrame
from pytest import raises

from infrastructure_planning.exceptions import ValidationError
from infrastructure_planning.preprocessors import (
    normalize_demand_point_table, DEMAND_POINT_TABLE_COLUMNS)


class TestNormalizeDemandPointTable():

    def test_reject_missing_column(self):
        for column in DEMAND_POINT_TABLE_COLUMNS:
            columns = list(DEMAND_POINT_TABLE_COLUMNS)
            columns.remove(column)
            table = DataFrame([], columns=columns)
            with raises(ValidationError):
                normalize_demand_point_table(table)

    def test_reject_missing_value(self):
        table = DataFrame([
            ('a', 1, 2, 3),
        ], columns=DEMAND_POINT_TABLE_COLUMNS)
        for column in DEMAND_POINT_TABLE_COLUMNS:
            t = table.copy()
            t[column][0] = float('nan')
            with raises(ValidationError):
                normalize_demand_point_table(t)

    def test_rename_population_year(self):
        d = normalize_demand_point_table(DataFrame([
            ('a', 1, 1, 1, 2000),
            ('b', 2, 2, 2, 2000),
            ('c', 3, 3, 3, 2000),
        ], columns=DEMAND_POINT_TABLE_COLUMNS + ['year']))
        table = d['demand_point_table']
        assert 'year' not in table.columns
        assert 'population_year' in table.columns

    def test_flatten_population_year(self):
        d = normalize_demand_point_table(DataFrame([
            ('a', 1, 1, 1, 2000),
            ('b', 2, 2, 2, 2000),
            ('c', 3, 3, 3, 2000),
            ('c', 3, 3, 4, 2001),
        ], columns=DEMAND_POINT_TABLE_COLUMNS + ['population_year']))
        table = d['demand_point_table']
        assert table[table['name'] == 'c']['population'].values[0] == 4
