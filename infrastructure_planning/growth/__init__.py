def get_future_years(target_year, past_years):
    past_years = sorted(past_years)
    future_years = range(int(past_years[-1]) + 1, target_year)
    if target_year not in past_years:
        future_years.append(target_year)
    return future_years
