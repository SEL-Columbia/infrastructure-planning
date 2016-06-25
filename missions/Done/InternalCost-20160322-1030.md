# Vision
Build second-generation infrastructure planning system.

# Mission
Write script to compute pre-network technology cost for grid.

# Owner
Roy Hyunjin Han

# Context
We want to compare the cost of producing electricities between different technologies and grid is the base of comparison.

# Timeframe
20160322-1030 - 20160322-1330: 180 minutes estimated

20160322-1030 - 20160328-1900: 6 days actual

# Objectives
1. + Compute transformer cost.
2. + Compute low voltage line and connection cost.
3. + Assemble and test script.

# Log
20160322-1030 - 20160322-1130

    + Compute transformer cost.
    + Estimate peak demand
        + Estimate maximum loss-adjusted production
    + Select transformer
    + Estimate transformer count
    + Get installation cost, maintenance cost per year, replacement cost per year

20160322-1130 - 20160322-1230

    + Compute low voltage line and connection cost.

20160322-1230 - 20160322-1330

    _ Assemble and test script.

20160323-1030 - 20160323-1230

    + Assemble and test script.

I am thinking about how to handle node-level overrides.

    _ Option 1: Each function specifies the whole table and node level arguments.

The problem with this option is that I won't know which node-level to give.

    _ Option 2: Each function specifies the local table and node level arguments.
    + Option 3: Each function just specifies node-level arguments.

The problem here is how do we handle cases where there is a time series for the given node? Maybe we can accept population_by_year

    + Decide nomenclature for node-level stuff.
        _ def f(table)
        _ def f(local_table)
        _ def f(demographic_table)
        def f(population)
        def f(population_by_year)

We can use either the inspect module or `func_code.co_varnames`. Let's use `func_code` for now.

    + Implement node-level override prototype.

Let's convert the script into a simpler version where each argument only appears once in the command line declaration and again in the function declaration.

    Option 1: Specify demographic table directly
    Option 2: Keep it in the dictionary

Is there ever a case when a function would want the entire table? If so, then we should keep it in g. Maybe an aggregate function might want it. So let's keep it in g.

I asked Edwin about variable costs. We'll have production cost vary by consumption, which varies by year.

20160323-1448

    + Option 1: Standardize all column names
    _ Option 2: Have function that constantly translates between my column name and their column name

20160323-1505 - 20160323-1605

20160323-1605 - 20160323-1635

    + Write function to compute `population_by_year`
    _ Make sure the whole script works properly

20160323-1645 - 20160323-1715

    + Make sure the whole script works properly
    + Convert a dictionary into a series
    + Convert multiple series into a dataframe

I'm not sure I did it in the most efficient way, but it works.

20160324-1100 - 20160324-1200

    + Estimate consumption by year
    + Decide whether `estimate_peak_demand_in_kw` takes `maximum_annual_consumption` or `consumption_by_year`

I think it should take `consumption_by_year`, just because we might want to take some average of yearly consumption.

    + Check whether order matters when computing peak demand and adjusting for losses

No, it does not because we are just using multiplication and division.

    + Change estimate population to use series
    + Change population by year into series
    + Change consumption by year into series

20160324-1526 - 20160324-1626

20160324-1656 - 20160324-1756

I don't think there is any clean way to compute the system costs in a separate function, unless I also let l/g e.g. v be a variable.

    + Option 1: Force each system cost module to be independent by only supplying the same arguments.
    _ Option 2: Trust that the author will not dip into results from another system cost module...

20160324-1730 - 20160324-1800

    + Implement `estimate_system_cost_by_technology`

    Option 1: Have each technology module return grid_xxx
    Option 2: Have each technology module return xxx and append `grid_` manually

Another question is whether we should nest the arguments or just flatten them out and hope for uniqueness. Python likes namespaces. But we can improvise by having the string be the namespace, kind of like the way redis does things.

20160325-1145 - 20160325-1245: 60 minutes

    _ Implement `estimate_grid_electricity_production_cost`
    _ Implement `estimate_grid_electricity_distribution_cost`

20160325-1500 - 20160325-1600: 60 minutes

    + Implement `estimate_grid_electricity_production_cost`
    _ Implement `estimate_grid_electricity_distribution_cost`

20160325-1630 - 20160325-1730: 60 minutes estimated

20160325-1630 - 20160325-1645: 15 minutes actual

    + Implement `compute_discounted_cash_flow`

20160325-1645 - 20160325-1745: 60 minutes estimated

    _ Implement `estimate_grid_electricity_distribution_cost`

I would like to think of an alternate name to ABBREVIATIONS.
Keys are what we are using to refer to the variable.
Values are what appears as column names in the table.

20160328

    + Implement `estimate_grid_electricity_distribution_cost`

20160328-1525 - 20160328-1625

    + Implement `estimate_grid_lv_line_cost`
    + Implement `estimate_grid_lv_connection_cost`

20160328-1645 - 20160328-1745

    + Implement `estimate_diesel_mini_grid_electricity_production_cost`
    + Implement `estimate_diesel_mini_grid_electricity_distribution_cost`
    + Implement `estimate_solar_home_electricity_production_cost`
    + Implement `estimate_solar_home_electricity_distribution_cost`

20160328-1800 - 20160328-1900

    + Implement `save_common_values`
    + Implement `save_unique_values`
    + Implement `sift_common_values`
