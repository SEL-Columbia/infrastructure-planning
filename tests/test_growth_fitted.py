import numpy as np
from infrastructure_planning.growth.fitted import get_fitted_linear_function


def test_get_fitted_linear_function():
    # If there is only one unique x, expect default_slope
    f = get_fitted_linear_function([(100, 100)], default_slope=5)
    assert np.isclose(f(100), 100)
    assert np.isclose(f(101), 105)
    f = get_fitted_linear_function([(100, 100), (100, 110)], default_slope=5)
    assert np.isclose(f(100), 105)
    assert np.isclose(f(101), 110)
    # If there is more than one unique x, expect fitted model
    f = get_fitted_linear_function([(0, 0), (1, 1)])
    assert np.isclose(f(0), 0)
    assert np.isclose(f(1), 1)
    f = get_fitted_linear_function([(0, 0), (0, 1), (1, 1), (1, 2)])
    assert np.isclose(f(0), 0.5)
    assert np.isclose(f(1), 1.5)
    f = get_fitted_linear_function([(0, 1), (1, 0), (2, 2), (3, 1)])
    assert np.isclose(f(0), 0.7)
    assert np.isclose(f(1), 0.9)
    assert np.allclose(f([0, 1]), [0.7, 0.9])  # Get ys from xs
