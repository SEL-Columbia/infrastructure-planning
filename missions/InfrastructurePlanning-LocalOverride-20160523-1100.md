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
The main goal will be to have trainers start testing the script.

    + Make sure that existing networks show
    + Fix geotable flip flop if wkt is specified wrong (or consider smart alignment)
    + Identify current output files

        common_values.csv
        edges.dbf
        edges.prj
        edges.shp
        edges.shx
        executive_summary.csv
        existing_networks.dbf
        existing_networks.prj
        existing_networks.shp
        existing_networks.shx
        grid_mv_line.csv
        infrastructure_graph.pkl
        infrastructure_streets_satellite.csv
        levelized_cost_by_technology.csv
        nodes-networker.csv
        nodes-sequencer.csv
        nodes.dbf
        nodes.prj
        nodes.shp
        nodes.shx
        result.cfg
        run.sh
        standard_error.log
        standard_output.log
        unique_values.csv
        unique_values_transposed.csv
        yearly_values.csv

    + Identify desired output files

        /result.cfg
        /run.sh
        /stdout.log
        /stderr.log
        /infrastructure_graph.pkl
        /infrastructure_map.csv
        /infrastructure_summary.csv
        /infrastructure_details.csv
        /estimate_total_cost/points.csv
        /estimate_total_cost/points.shp
        /estimate_total_cost/lines.csv
        /estimate_total_cost/lines-existing.shp
        /estimate_total_cost/lines-proposed.shp
        /estimate_total_cost/costs.csv
        /estimate_total_cost/parameters.json

# Tasks

    Clean up files in output folder
        Generate executive summary as specified by Naichen and Edwin

    Fix bugs
        Rename to existing grid mv line and proposed grid mv line
        Change instances of $/kW to cost per kW
        Change finance units to years explicitly

        Fix input to sequencer to use only points selected for grid
        Fix AttributeError: 'NoneType' object has no attribute 'is_aligned' for random geolocated cities
        Use number of people per connection

    Add credits to each tool
    Make JSON file for Nigeria dataset

    Check whether local overrides work
        Expose minimum node count per subnetwork
        Expose maximum_connection_count
        Expose maximum_consumption_per_year_in_kwh

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
            Submit pull request to networker
        sequence_total_grid_mv_network
            Submit pull request to sequencer
        estimate_nodal_external_cost_by_technology
            estimate_grid_external_cost
            estimate_diesel_mini_grid_external_cost
            estimate_solar_home_external_cost
        estimate_total_cost

    Setup laptop
    Setup independent cloud server
