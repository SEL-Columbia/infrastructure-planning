import numpy as np
from sklearn.linear_model import LinearRegression


def get_fitted_linear_function(xys, default_slope=0):
    xs, ys = zip(*xys)
    if len(set(xs)) == 1:
        xs = list(xs) + [xs[0] + 1]
        ys = list(ys) + [np.mean(ys) + default_slope]
    model = LinearRegression()
    model.fit(np.array(xs).reshape(-1, 1), ys)
    slope = model.coef_[0]
    y_intercept = model.intercept_
    return lambda x: slope * np.array(x) + y_intercept
