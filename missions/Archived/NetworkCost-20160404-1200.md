# Vision
Build second-generation infrastructure planning system.

# Mission
Integrate existing cost to estimate network cost.

# Owner
Roy Hyunjin Han

# Context
Building and sequencing a network is an important part of planning infrastructure.

# Timeframe
20160404-1300 - 20160404-1500: 2 hours estimated

20160404-1300 - 20160506-1300: 32 days actual

# Objectives
1. Run networker
2. Run sequencer
3. Integrate networker and sequencer

# Log
20160404-1200 - 20160404-1215

Clone both repositories.

- https://github.com/SEL-Columbia/networker
- https://github.com/SEL-Columbia/Sequencer

20160404-1530

Well, I managed to get them both working, with some fixes.

However, the code looks pretty messy.

20160404-1600 - 20160404-1700

    + Fork repositories.
    + Get them working.
        + Fix networker
            + Remove numba.jit
        + Fix sequencer
    + Commit.
    + Write a script that runs the networker and sequencer.

20160405-1100 - 20160405-1200

20160406-1400 - 20160406-1600

    + Write a script that runs the networker and sequencer.
    + Decide name for population column.

        _ population start
        _ population end

        _ starting population
        _ ending population

        _ 2008 population
        _ 2020 population

        _ population in 2008
        _ population in 2020

        _ population (2008)
        _ population (2020)

        _ consumption (kWh)
        _ Consumption in kWh

        year
        population year
        2010
        population
        population in 2010
        population (2010)
        2000000
        financing year
        2020
        projected population
        population in 2020
        population (2020)
        3939393

        = year, population, financing year, future population, future consumption
        year, population, financing year, population++, consumption++
        year, population, financing year, effective population, effective consumption
        _ year, population, financing year, projected population, projected consumption

        _ population (2010), population (2020), consumption (2010), consumption (2020)

        population (2010)
        2000000
        population (2020)
        3939393

        _ financing year
        _ financing population

        _ effective year
        _ effective population

        _ initial population
        _ population

        _ consumption (2008 kWh)
        _ Consumption in kWh in 2008
        Consumption (kWh, 2008)

        population
        projected population

The year based columns is not going to work because the population column might be different for each node.

I choose this nomenclature because we can feed it back into the system. And future is a positive word.

    + year, population, financing year, future population, future consumption

Instead, let's just have duplicate columns marked by an asterisk?

No, I don't like symbolism. Let's be explicit and call it Future.

20160406-1700 - 20160406-1900

20160407-1100 - 20160407-1200

    + List tasks remaining.

20160407-1400 - 20160407-1500

20160407-1500 - 20160407-1630

    + Compute network budget.

        _ estimate_system_cost_by_technology
        estimate_system_cost_by_technology_before_grid_mv_network
        _ estimate_system_cost_by_technology_before_mv_network
        _ estimate_system_cost_by_technology_before_network

        estimate_grid_mv_network_budget
        _ estimate_network_budget

        # minimize_grid_mv_line
        # optimize_grid_mv_network
        # propose_grid_mv_network_using_modified_boruvka,
        suggest_grid_mv_network_using_modified_boruvka,

        estimate_grid_mv_line_budget_in_meters,
        estimate_grid_mv_network_budget_in_meters,

        place_grid_mv_line_using_modified_boruvka,
        place_grid_mv_network_using_modified_boruvka,
        suggest_grid_mv_network_using_modified_boruvka,

        # sequence_grid_mv_network
        # order_grid_mv_network_construction

20160408-1200 - 20160408-1300

20160408-1430 - 20160408-1530

    + Run networker.

I want a table to be available for each main function.
I want node-level overrides to work.

I think I need to decide how I want downstream functions to work.
And what about a graph?

    def assemble_grid_mv_network():
    def assemble_grid_mv_network(table):
    def assemble_grid_mv_network(result_table):
    def assemble_grid_mv_network(x_column, y_column, ...):
        pass

The thing is that downstream functions don't need to go name by name...

So maybe we should have a portion that is node level and another portion that is not?

Or maybe we should detect whether a function needs node-level or table or shapefile and feed it accordingly? I like this.

    # assemble_grid_mv_network takes a table
    # sequence_grid_mv_network takes a graph
    # estimate_total_cost takes a graph

    # Compute
    for f in MAIN_FUNCTIONS:
        for name, table in g['demographic_table'].groupby('name'):
            l = OrderedDict({'name': name}, **get_local_arguments(table))

            # Separate outputs from inputs

            results = compute

        # Reassemble table here, perhaps by concatenating columns?
        # The issue is that there could be multiple columns added
        # The other option is to only assemble something on demand if it is requested

    ls = []
        try:
            l.update(compute(f, l, g))
        except InfrastructurePlanningError as e:
            exit('%s.error = %s : %s : %s' % (
                e[0], name.encode('utf-8'), f.func_name, e[1]))
    ls.append(l)

Decide nodal vs total

    estimate_nodal_population,
    estimate_nodal_consumption_in_kwh,
    estimate_nodal_peak_demand_in_kw,
    estimate_nodal_system_cost_by_technology,
    estimate_nodal_grid_mv_network_budget_in_meters,
    assemble_total_grid_mv_network,
    sequence_total_grid_mv_network,
    estimate_total_cost,

Should we support multiple years within a location? No.

    + Rename system to internal
    + Remove references to pre network
    + Rename distribution cost to internal distribution cost
    + Remove references to OrderedDict

20160411-1300 - 20160411-1400

    + Write pseudocode for `assemble_total_grid_mv_network`

20160411-1400 - 20160411-1500

    + See what information is included in edges.shp and nodes.shp by networker
    + Integrate metric, networker, sequencer into one script.
        + Run networker.
        + Run sequencer.
        + Extract relevant columns from sequencer output.

20160504-1630 - 20160504-1730

    + Map network nodes and edges
    + Integrate existing grid
        + Use old np datasets

20160506-1100 - 20160506-1200

    + Draft tool template
    + Add bird distance vs multiplier option
    + Aggregate costs for each node to compute total discounted and levelized cost
    + Check that it works
    + Draft result template
