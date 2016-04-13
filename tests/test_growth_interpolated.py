import numpy as np
from infrastructure_planning.growth.interpolated import (
    get_interpolated_spline_extrapolated_linear_function)


def test_get_interpolated_spline_extrapolated_linear_function():
    # If there is only one unique x, expect default_slope
    f = get_interpolated_spline_extrapolated_linear_function(
        [(100, 100)], default_slope=5)
    assert np.isclose(f(102), 110)
    # If x is inside the interpolated domain, y should match original
    # If x is on the left, y should extend the trend from the leftmost point
    # If x is on the right, y should extend the trend from the rightmost point
    f = get_interpolated_spline_extrapolated_linear_function(
        [(100, 1), (300, 2), (500, 5)])
    assert np.isclose(f(300), 2)
    assert np.isclose(f(99), 0.99)
    assert np.isclose(f(501), 5.01)
    assert np.allclose(f([300, 99, 501]), [2, 0.99, 5.01])  # Get ys from xs
