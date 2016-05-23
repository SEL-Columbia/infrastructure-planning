# Vision
Build second-generation infrastructure planning system.

# Mission
Make sure that local overrides work for key variables.

# Owner
Roy Hyunjin Han

# Context
The user must be able to override variables on a case by case basis.

# Timeframe
20160523-1130 - 20160526-1130: 3 days estimated

# Objectives
1. Identify key variables.
2. Make sure that local overrides for key variables work.
3. Make sure the script accepts parameters in JSON format.

# Log
20160523-1130 - 20160523-1230

# Tasks

    Fix bugs
        Make sure that existing networks show
        Fix geotable flip flop if wkt is specified wrong (or consider smart alignment)
        Rename to existing grid mv line and proposed grid mv line
        Fix input to sequencer to use only points selected for grid
        Fix AttributeError: 'NoneType' object has no attribute 'is_aligned' for random geolocated cities
        Change instances of $/kW to cost per kW
        Use number of people per connection
        Change finance units to years explicitly

    Add credits to each tool
    Make JSON file for Nigeria dataset

    Check whether local overrides work
        Expose minimum node count per subnetwork
        Expose maximum_connection_count
        Expose maximum_consumption_per_year_in_kwh

    Generate executive summary as specified by Naichen and Edwin

    Split components into package and separate tools
        estimate_nodal_population
        estimate_nodal_consumption_in_kwh
        estimate_nodal_peak_demand_in_kw
        estimate_nodal_internal_cost_by_technology
            estimate_grid_internal_cost
            estimate_diesel_mini_grid_internal_cost
            estimate_solar_home_internal_cost
        estimate_nodal_grid_mv_network_budget_in_meters
        assemble_total_grid_mv_network
        sequence_total_grid_mv_network
        estimate_nodal_external_cost_by_technology
            estimate_grid_external_cost
            estimate_diesel_mini_grid_external_cost
            estimate_solar_home_external_cost
        estimate_total_cost

    Setup laptop
    Setup independent cloud server
