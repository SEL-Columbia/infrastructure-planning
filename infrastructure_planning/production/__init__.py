from math import ceil


def adjust_for_losses(x, *fractional_losses):

    def adjust_for_loss(x, fractional_loss):
        divisor = 1 - fractional_loss
        if not divisor:
            return x
        return x / float(divisor)

    y = x
    for fractional_loss in fractional_losses:
        y = adjust_for_loss(y, fractional_loss)
    return y


def prepare_actual_system_capacity(
        desired_system_capacity, option_table, capacity_column):
    t = option_table
    # Select option
    eligible_t = t[t[capacity_column] < desired_system_capacity]
    if len(eligible_t):
        t = eligible_t
        # Choose the largest capacity from eligible types
        selected_t = t[t[capacity_column] == t[capacity_column].max()]
    else:
        # Choose the smallest capacity from all types
        selected_t = t[t[capacity_column] == t[capacity_column].min()]
    selected = selected_t.ix[selected_t.index[0]]
    # Get capacity and count
    selected_capacity = selected[capacity_column]
    selected_count = int(ceil(desired_system_capacity / float(
        selected_capacity)))
    actual_system_capacity = selected_capacity * selected_count
    # Get costs
    installation_lm_cost = selected_count * selected['installation_lm_cost']
    maintenance_lm_cost_per_year = selected_count * selected[
        'maintenance_lm_cost_per_year']
    replacement_lm_cost_per_year = installation_lm_cost / float(selected[
        'lifetime_in_years'])
    return [
        ('desired_system_' + capacity_column, desired_system_capacity),
        ('selected_' + capacity_column, selected_capacity),
        ('selected_count', selected_count),
        ('actual_system_' + capacity_column, actual_system_capacity),
        ('installation_lm_cost', installation_lm_cost),
        ('maintenance_lm_cost_per_year', maintenance_lm_cost_per_year),
        ('replacement_lm_cost_per_year', replacement_lm_cost_per_year),
    ]
