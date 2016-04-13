import numpy as np
from sklearn.linear_model import LinearRegression

from . import split_xys


def get_fitted_linear_function(xys, default_slope=0):
    xs, ys = split_xys(xys, default_slope)
    model = LinearRegression()
    model.fit(np.array(xs).reshape(-1, 1), ys)
    slope = model.coef_[0]
    y_intercept = model.intercept_
    return lambda x: slope * np.array(x) + y_intercept
