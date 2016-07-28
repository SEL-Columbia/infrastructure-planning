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

    g = save_parameters(args.__dict__, __file__)
    g = load_parameters(g)

    g = load_parameters(args.__dict__, __file__)
    save_parameters(g)

    g = load_and_save_parameters(args.__dict__, __file__)

	Generate arguments folder
        /arguments/parameters.json

# Tasks

	Generate points.csv
	Generate points.shp
	Generate lines.csv
	Generate lines-existing.shp
	Generate lines-proposed.shp

	Remove edges.* intermediate files
	Rename executive_summary to infrastructure-summary
	Remove grid_mv_line table
	Remove nodes* intermediate files
	Rename standard_output.log to stdout.log
	Rename standard_error.log to stderr.log
	Rename levelized_cost_by_technology to infrastructure-details

    Update output files
        Include essential properties in shapefile
            https://github.com/SEL-Columbia/infrastructure-planning/issues/3
            Check shapefile column name length limit
        Clean up output folder
            + /result.cfg
            + /run.sh
            /stdout.log
            /stderr.log
            /infrastructure-graph.json

            = /arguments/parameters.json
            /arguments/selected-technologies.txt
            /arguments/demand-points.csv
            /arguments/connection-types.csv
            /arguments/grid-mv-lines.csv
            /arguments/grid-mv-transformers.csv
            /arguments/diesel-mini-grid-generators.csv
            /arguments/solar-home-panels.csv
            /arguments/solar-mini-grid-panels.csv

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
        git diff 2115bb0aeecf5e6e0b15d2a37513294aa0874f8e | grep diff
        diff --git a/.gitignore b/.gitignore
        diff --git a/demo_sequencer.py b/demo_sequencer.py
        diff --git a/requirements.txt b/requirements.txt
        diff --git a/sequencer/Models.py b/sequencer/Models.py
        diff --git a/sequencer/NetworkPlan.py b/sequencer/NetworkPlan.py
        diff --git a/sequencer/Sequencer.py b/sequencer/Sequencer.py
        diff --git a/sequencer/Utils.py b/sequencer/Utils.py

    Separate calculator and aggregator
        Have calculator generate geojson file

    Prepare for production
        Write positive test

    Update interface
        Show overrided columns
        Let user download example table for each table
        Add acknowledgments to integrated tool
        Look into issues with live table override
        Show simple map in addition to satellite map
        Make existing grid a different color or stroke
        Consider letting user add row or column

    Update validation
        https://github.com/SEL-Columbia/infrastructure-planning/issues/5
        Consider sending error messages on invalid numbers with commas

    Add instructions on how to set up the system on a new machine
    Test that local override for household consumption works
    Test that blank entries in local override columns use global value
