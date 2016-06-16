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

20160523-1130 - 20160613-1800: 20 days actual

# Objectives
1. + Identify key variables.
2. + Make sure that local overrides for key variables work.
3. + Make sure the script accepts parameters in JSON format.

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
    _ def save_parameters
    _ def normalize_parameters(g, table_names, target_folder):
    _ def normalize_parameters(table_names, target_folder, g):
    _ def normalize_parameters(target_folder, table_names, g):

Maybe I'll change my notation from underscore for cancelling something to the hash symbol, the universal comment character.

    + Implement normalize_parameters
    + Update normalize_column_names

20160524-1130 - 20160524-1230: 1 hour estimated
20160524-1130 - 20160524-1600: 4 hours 30 minutes actual

I should really finish the JSON support today for CJN.

    + Implement normalize_grid_mv_line_geotable
    + Clean up existing_networks_latlon scotch tape
    + Rename demographic_table to demand_point_table or point_table

Will there ever be a case when medium voltage lines are for some other technology, not grid? But to be consistent, there is always grid in front of mv line.

    existing_grid_mv_line_shapefile
    _ existing_mv_line_shapefile
    _ existing_grid_mv_lines_shapefile
    _ existing_mv_lines_shapefile
    _ existing_mv_shapefile

I'm not sure whether I should pass around grid_mv_lines or grid_mv_line_geotable. The problem with shapely geometries is that they do not naturally support other attributes that might have been passed in for each line and that we might want to use or preserve. In that case, let's stick to grid_mv_line_geotable.

20160524-1600 - 20160524-1700: 1 hour estimated

Since we only have an hour left, let's jump to making the JSON file for the Nigeria dataset.

20160525-1400 - 20160525-1500

+ Rename files

    senegal-selected-demand-points.csv
    senegal-selected-grid-mv-lines.csv
    _ senegal-selected-points.csv
    _ senegal-selected-lines.csv
    _ senegal-existing-grid-mv-lines.csv
    _ senegal-demand-points
    _ senegal-grid-mv-lines
    _ senegal-some-demand-points
    _ senegal-some-grid-mv-lines.csv

The disadvantage to using hashes is that it might confuse people when we are also using hashes for section headers.

20160525-1600 - 20160525-1700

We can use the configuration file as a starting point. The script should load the JSON, then either call run or construct an argument_parser. I think calling run is better. I see, it loads a ``g`` which is short for global variables. The JSON should become g, but there will also be some work where relative paths are resolved to source_folder.

It looks like there is an option for nested JSON.

Option 1: Nest the JSON into sections, with keys truncated and later prepended with their section name (but that would require adding extra text to the beginning of some keys).

Option 2: Do not truncate the keys.

For now, let's just keep it flat, get it working and think about this later.

20160526-1100 - 20160526-1200

There are two issues:

1. For some reason, grid mv external cost is constant across all nodes. This is a bug.

The issue happens when computing grid external cost. I called it as local/nodal when it was coded as total.

    Option 1a: Change code so that it really is local.
    _ Option 1b: Just make it run as total.

2. I also need to integrate line adjustment factor into the budget.

    Option 2a: Divide the budget by the line adjustment factor.
    _ Option 2b: Send line adjustment factor to networker and multiply each distance by the adjustment factor.

I think option 2a is acceptable.

    + Rename nodal to local

20160527-1200 - 20160527-1300

I keep getting distracted.

20160527-1400 - 20160527-1700

    + Check that yesterday's fix actually made grid mv external cost variable
    + Fix input to sequencer to use only points selected for grid
        + Check why grid mv external cost is constant
    + Think of how to integrate line adjustment factor
    + Use number of people per connection

I'm not sure what I meant by "Change finance units to years explicitly." It looks like all the finance stuff is in years already and I might have done this and forgotten about it.

    _ from infrastructure_planning.utilities import compute
    _ from infrastructure_planning.utils import compute
    _ from infrastructure_planning.funcs import compute
    _ from infrastructure_planning.functions import compute
    from infrastructure_planning.macros import compute
    _ from infrastructure_planning.meta import compute

    _ from infrastructure_planning.resource.electricity import
    _ from infrastructure_planning.resource.water import
    _ from infrastructure_planning.resource.capacity import
    _ from infrastructure_planning.resource.loss import

    _ from infrastructure_planning.capacity import
    _ from infrastructure_planning.loss import

    from infrastructure_planning.electricity import
    from infrastructure_planning.water import
    from infrastructure_planning.production import adjust_for_losses

    + Add selected_technologies argument

20160527-2100 - 20160527-2200

I just realized that levelized cost for grid is meaningless if there is no external component.

20160527-2200 - 20160527-2300

    + Select grid if it is connected, otherwise choose standalone

20160528-1500 - 20160528-2000

    + Remove duplicate required columns
    _ Split transpose across multiple files

20160528-2100 - 20160528-2300

    + Generate glossary of variable names using one example
    + Expose minimum node count per subnetwork

        _ grid_mv_minimum_node_count_per_subnetwork
        _ grid_mv_minimum_network_size
        _ grid_mv_network_minimum_node_count
        grid_mv_network_minimum_point_count
        _ grid_mv_network_point_minimum_count
        _ grid_mv_network_point_count_minimum
        _ grid_mv_network_minimum_size

    + Expose connection_count
    + Expose consumption_per_year_in_kwh
    + Expose proposed_cost_per_connection
    + Generate executive summary as specified by Naichen and Edwin

20160529-0000 - 20160528-0130

    + Check whether local overrides work

20160610-1530 - 20160610-1700: 90 minutes

    _ as_json
    json
    _ render_json
    _ show_json

20160613-1600 - 20160613-1700: 1 hour

Let's start by making a dummy JSON file.

    + Make a dummy JSON file
    + Adjust script so that it accepts alternate ways to specify source_folder and target_folder
    + Accept JSON file as first argument

If a source_folder is specified, then adjust relative paths accordingly.

    + Support relative paths using source_folder

If a configuration path is specified, then use it.

    + Adjust script so that it accepts JSON file

20160613-1800
