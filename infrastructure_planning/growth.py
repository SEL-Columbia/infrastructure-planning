import numpy as np
from sklearn.linear_model import LinearRegression


prepare_xs = lambda x: np.array(x).reshape(-1, 1)


def get_future_years(target_year, year_packs):
    past_years = sorted(int(x[0]) for x in year_packs)
    future_years = range(past_years[-1] + 1, target_year)
    if target_year not in past_years:
        future_years.append(target_year)
    return future_years


def get_linear_model(time_series, default_growth_percent):
    'Fit linear model on time_series'
    time_packs = _get_time_packs(time_series)
    default_growth_factor = 1 + default_growth_percent / 100.
    model = LinearRegression()
    if len(time_packs) == 1:
        time, value = time_packs[-1]
        times = [time, time + 1]
        values = [value, value * default_growth_factor]
    else:
        time_array = np.array(time_packs)
        times = time_array[:, 0]
        values = time_array[:, 1]
    model.fit(prepare_xs(times), values)
    return model


def _get_time_packs(time_series):
    'Convert series into list of tuples'
    if hasattr(time_series, 'values'):
        time_count = len(time_series)
        xs = time_series.index.values.reshape(time_count, 1)
        ys = time_series.values
        time_packs = zip(xs, ys)
    else:
        time_packs = time_series
    return time_packs
