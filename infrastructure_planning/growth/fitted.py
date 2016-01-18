import numpy as np
from sklearn.linear_model import LinearRegression


def get_fitted_linear_function(xys, default_slope=0):
    xys = np.array(xys)
    xs, ys = xys[:, 0], xys[:, 1]
    model = LinearRegression()
    model.fit(xs.reshape(-1, 1), ys)
    slope = model.coef_[0] if len(set(xs)) > 1 else default_slope
    y_intercept = model.intercept_
    return lambda x: slope * np.array(x) + y_intercept
