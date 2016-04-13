import numpy as np
from scipy.interpolate import interp1d
from sklearn.linear_model import LinearRegression

from . import split_xys


def get_interpolated_spline_extrapolated_linear_function(xys, default_slope=0):
    xs, ys = split_xys(xys, default_slope)
    middle_function = interp1d(xs, ys, kind='linear')
    # Find intercepts
    regression_model = LinearRegression()
    regression_model.fit(np.array(xs).reshape(-1, 1), ys)
    slope = regression_model.coef_[0]
    x_min, x_max = min(xs), max(xs)
    left_intercept = middle_function(x_min) - slope * x_min
    right_intercept = middle_function(x_max) - slope * x_max
    # Define functions for left, middle, right
    left_function = lambda x: slope * x + left_intercept
    right_function = lambda x: slope * x + right_intercept

    def f(x):
        x = np.array(x)
        y = np.zeros(x.shape)
        # Define boolean masks
        x_left = x < x_min
        x_middle = (x_min <= x) & (x <= x_max)
        x_right = x_max < x
        # Compute y
        y[x_left] = left_function(x[x_left])
        y[x_middle] = middle_function(x[x_middle])
        y[x_right] = right_function(x[x_right])
        return y

    return f
