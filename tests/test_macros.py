import pytest
from infrastructure_planning.macros import interpolate_values
from pandas import DataFrame


SOURCE_TABLE = DataFrame([
    [1, 100],
    [5, 500],
], columns=[
    'x', 'y',
])


@pytest.mark.parametrize('x, y', [
    (0, 100),
    (1, 100),
    (2, 200),
    (3, 300),
    (4, 400),
    (5, 500),
    (6, 500),
])
def test_interpolate_values(x, y):
    assert interpolate_values(SOURCE_TABLE, 'x', x)['y'] == y
