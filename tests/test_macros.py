import pytest
from infrastructure_planning.macros import interpolate_values
from pandas import DataFrame


SOURCE_TABLE = DataFrame([
    [2, 200],
    [6, 600],
], columns=[
    'x', 'y',
])


@pytest.mark.parametrize('x, y', [
    (0, 200),
    (1, 200),
    (2, 200),
    (3, 300),
    (4, 400),
    (5, 500),
    (6, 600),
    (7, 600),
])
def test_interpolate_values(x, y):
    assert interpolate_values(SOURCE_TABLE, 'x', x)['y'] == y
