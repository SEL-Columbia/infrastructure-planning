# Vision
Build second-generation infrastructure planning system.

# Mission
Prepare system for first production release.

# Owner
Roy Hyunjin Han

# Context
It is important to freeze work in a finished state in order to make it easy to pick up again later.

# Timeframe
20160711-1700 - 20160729-1700: 18 days estimated

# Objectives
1. + Fix bugs
2. Update output files
3. Update executive summary by technology

# Log
20160711-1700 - 20160711-1800: 1 hour

    + Increase size of smallest point radius
    + Allow local override for unit household consumption
    + Let user override consumption by connection type

20160711-1945 - 20160711-1845: 1 hour

    + Add connection type local override column names to glossary
    + Make sure blank entries in local override columns correctly use global value
    + Add column name to empty columns
    + Check that table sorts properly in standard spreadsheet programs

20160711-2115 - 20160711-2200: 45 minutes

    + Get rid of underscores in columns
    + Fix mv line assignments to node for mv lines to fake points
    + Provide better error messages when a column is missing
    + Fix AttributeError: 'NoneType' object has no attribute 'is_aligned' for random geolocated cities

Note that the AttributeError bug was fixed in https://github.com/SEL-Columbia/networker/pull/91

20160712-1400

    market_consumption_in_kwh_per_year_per_market
    _ consumption_in_kwh_per_year_per_market
    _ market_consumption_in_kwh_per_year
    _ market_consumption_in_kwh_per_year_per_connection
    _ market_consumption_in_kwh_per_year_per_unit
    _ market_unit_consumption_in_kwh_per_year
    _ single_market_consumption_in_kwh_per_year

20160718-1615 - 20160718-1645: 30 minutes

Let's run the default example and check whether we have duplicate keys anywhere.

    + Check duplicate keys in costs, examples, glossary

20160725-1600 - 20160725-1700: 1 hour

    + Check pull request for networker
    + Review which keys are duplicate
        grid_mv_line_installation_lm_cost_per_meter
        grid_mv_line_maintenance_lm_cost_per_meter_per_year

The duplicates are appearing because the keys are appearing both in ls and g. Specifically, the following function is returning the keys verbatim in order to use ``prepare_component_cost_by_year``.

    estimate_grid_mv_line_cost_per_meter

20160725-1715 - 20160725-1745: 30 minutes

    + Rename to existing mv line and proposed mv line

Let's look at what is currently in the output folder and make a list of tasks.

	.
	├── edges.dbf
	├── edges.prj
	├── edges.shp
	├── edges.shx
	├── executive_summary.csv
	├── grid_mv_line.csv
	├── infrastructure_graph.pkl
	├── infrastructure_map.csv
	├── levelized_cost_by_technology.csv
	├── nodes.dbf
	├── nodes-networker.csv
	├── nodes.prj
	├── nodes-sequencer.csv
	├── nodes.shp
	├── nodes.shx
	├── result.cfg
	├── run.sh
	└── summary
		├── costs.csv
		├── examples.csv
		└── glossary.csv

20160726-1700 - 20160726-1730: 30 minutes

I have about three hours. Let's aim to clean up the output files today.

20160727-1715 - 20160727-1745: 30 minutes

20160727-1815 - 20160727-1845: 30 minutes

    _ g = save_parameters(args.__dict__, __file__)
    _ g = load_parameters(g)

    _ g = load_parameters(args.__dict__, __file__)
    _ save_parameters(g)

    g = load_and_save_parameters(args.__dict__, __file__)
    _ g = prepare_parameters

20160728-1400 - 20160728-1430: 30 minutes

    + Generate /arguments/parameters.json
	+ Generate /arguments folder

20160729-1630 - 20160729-1700: 30 minutes

    + Port load_geotable
    + Improve controlled error handling and error messages

20160730-1745 - 20160729-1800: 15 minutes

20160830-1630 - 20160830-1645: 15 minutes

20160906-1515 - 20160906-1530: 15 minutes

Let's try to remember what we were doing here.

    _ selected_technologies.txt
    selected_technologies_text.txt

    + Use a modification of the key name for argument file name

20160906-1630 - 20160906-1645: 15 minutes

20160906-1700 - 20160906-1715: 15 minutes

    + Change population_growth_as_percent_of_population_per_year to float
    + Show standard error and standard output

20160908-1200 - 20160908-1215: 15 minutes

20160913-1630 - 20160913-1645: 15 minutes

20160915-1600 - 20160915-1630: 30 minutes

    Review goals

# Tasks

    Check for required columns like name
    Replace geopy geocoding with error message about expected longitude latitude
	Generate points.csv
	Generate points.shp
	Generate lines.csv
	Generate lines-existing.shp
	Generate lines-proposed.shp
	Remove edges* intermediate files
	Remove grid_mv_line table
	Remove nodes* intermediate files

    Generate intermediate and yearly value files for debugging
	Rename standard_output.log to stdout.log
	Rename standard_error.log to stderr.log
	Rename executive_summary to interface/summary.csv
	Rename levelized_cost_by_technology to interface/details.csv

    Clean up output folder
        + /result.cfg
        + /run.sh
        /stdout.log
        /stderr.log
        /infrastructure-graph.json

        + /arguments/arguments.json
        + /arguments/connection-types.csv
        + /arguments/demand-points.csv
        + /arguments/diesel-mini-grid-generators.csv
        + /arguments/grid-mv-lines.csv
        + /arguments/grid-mv-transformers.csv
        + /arguments/selected-technologies.txt
        + /arguments/solar-home-panels.csv
        + /arguments/solar-mini-grid-panels.csv

        /properties/points.csv
        /properties/points.shp
        /properties/lines.csv
        /properties/lines-existing.shp
        /properties/lines-proposed.shp
        /properties/costs.csv
        /properties/examples.csv
        /properties/glossary.csv
        /interface/map.csv
        /interface/summary.csv
        /interface/details.csv

    Include essential properties in shapefile
        https://github.com/SEL-Columbia/infrastructure-planning/issues/3
        Check shapefile column name length limit

    Update executive summary by technology
        Show initial
        Show projected recurring
        Show levelized cost
        Show location count
        Show connection count
        Show population count
        Show initial cost per connection

    Update model
        Consider estimating population growth using projected population year
		Consider total population and % connected to compute (unconnected) household count as suggested by Edwin

    Submit pull request for sequencer
    Separate calculator and aggregator
    Write positive test

    Update interface
        Show overrided columns
        Let user download example table for each table
        Add acknowledgments to integrated tool
        Look into issues with live table override
        Show simple map in addition to satellite map
        Make existing grid a different color or stroke
        Consider letting user add row or column

    Add instructions on how to set up the system on a new machine
    Add warning if peak_demand_in_kw is nan or zero
    Use global value if local value is nan

    Support capacity and installation cost per kw override
    Support multiple transformer subtables
    Convert tool into notebook

    Update system size algorithm
        Have user specify generator capacity
        Have user specify generator purchase price
        Have user specify generator installation cost per kw
        Have user specify maintenance cost per year as fraction of purchase price
        Get desired system capacity
        Add system capacity safety factor
        Compute purchase price per kw
        Pick nearest generator capacity and use those prices per kw
        Round actual capacity to integer
