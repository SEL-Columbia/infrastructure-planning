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
        /infrastructure_map.csv
        /infrastructure_summary.csv
        /infrastructure_details.csv
        /infrastructure_graph.pkl (eventually topojson)
        /estimate_total_cost/points.csv
        /estimate_total_cost/points.shp
        /estimate_total_cost/lines.csv
        /estimate_total_cost/lines-existing.shp
        /estimate_total_cost/lines-proposed.shp
        /estimate_total_cost/costs.csv
        /estimate_total_cost/parameters.json

20160523-1430 - 20160523-1530

The main goal is to make sure the users can start testing tomorrow. I'm really tempted to start cleaning up the code, but I should hold off on that temptation and just fix the bugs.

    + Change instances of $/kWh to cost per kWh

The original purpose of existing_networks_latlon was to detect whether the existing networks needed to have its coordinates reversed.  It would be nice if the existing networks were just specified in latitude and longitude explicitly. There is also the complication that Mapbox wants longitude, latitude. It's possible we are having this problem because of WKT format, which leaves coordinate order ambiguous. Maybe there should be something to indicate which coordinate order the file is using. Let's stick to longitude, latitude.

Make sure that we normalize points and lines to Longitude, Latitude. Ideally, this should happen at the beginning and not only when it is needed.

    g = normalize_parameters(target_folder, g)
    _ g = normalize_everything(target_folder, g)
    _ g = normalize(target_folder, g)

Normalize and save raw inputs? No, I don't think we need to save the raw inputs.

I don't think that estimate_total_cost should produce the final outputs. There should be some kind of reporting function.

    generate_total_summary
    _ aggregate
    _ save
    _ summarize

20160523-1800 - 20160523-1900

I don't like it when functions depend on global variables because then they are hard to test.

    def normalize_parameters(g, table_names):
    # def save_parameters
    # def normalize_parameters(g, table_names, target_folder):
    # def normalize_parameters(table_names, target_folder, g):
    # def normalize_parameters(target_folder, table_names, g):

Maybe I'll change my notation from underscore for cancelling something to the hash symbol, the universal comment character.

    + Implement normalize_parameters
    + Update normalize_column_names

20160524-1130 - 20160524-1230: 1 hour estimated
20160524-1130 - 20160524-1600: 4 hours 30 minutes actual

I should really finish the JSON support today for CJN.

    + Implement normalize_grid_mv_line_geotable
    + Clean up existing_networks_latlon scotch tape

Will there ever be a case when medium voltage lines are for some other technology, not grid? But to be consistent, there is always grid in front of mv line.

    existing_grid_mv_line_shapefile
    # existing_mv_line_shapefile
    # existing_grid_mv_lines_shapefile
    # existing_mv_lines_shapefile
    # existing_mv_shapefile

I'm not sure whether I should pass around grid_mv_lines or grid_mv_line_geotable. The problem with shapely geometries is that they do not naturally support other attributes that might have been passed in for each line and that we might want to use or preserve. In that case, let's stick to grid_mv_line_geotable.

# Tasks

    = Fix bugs
        Use number of people per connection

    Make JSON file for Nigeria dataset

    Fix more bugs
        Fix input to sequencer to use only points selected for grid
        Change finance units to years explicitly

    Check whether local overrides work
        Expose minimum node count per subnetwork
        Expose maximum_connection_count
        Expose maximum_consumption_per_year_in_kwh

    Clean up output folder
        /result.cfg
        /run.sh
        /stdout.log
        /stderr.log
        /infrastructure_map.csv
        /infrastructure_summary.csv
        /infrastructure_details.csv
        /infrastructure_graph.pkl (eventually topojson)
        /summary/parameters.json
        /summary/points.csv
        /summary/points.shp
        /summary/lines.csv
        /summary/lines-existing.shp
        /summary/lines-proposed.shp
        /summary/costs.csv
            Generate executive summary as specified by Naichen and Edwin
    Consider saving the input and output for each function for debugging purposes (we can do this in compute)

    Add acknowledgments to integrated tool
    Setup independent cloud server
    Setup laptop

    Fix miscellaneous issues
        Fix AttributeError: 'NoneType' object has no attribute 'is_aligned' for random geolocated cities
        Rename to existing mv line and proposed mv line
        Consider renaming demographic_table to demand_point_table or point_table

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

    Add acknowledgments to separate tools
