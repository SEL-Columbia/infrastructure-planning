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

20160919-1015 - 20160919-1045: 30 minutes

    + Look at Naichen's presentation
    + Identify proposed cost per household (it is proposed cost per connection)
    + Extract goals from GitHub

20160919-1130 - 20160919-1200: 30 minutes

I think that putting things into notebook format will be important for rapid development, both now and in the future.

    + Sort goals from TODO.goals

20160919-1500 - 20160919-1530: 30 minutes

20160919-1600 - 20160919-1630: 30 minutes

    + Write simple jupyter notebook
    + Write bash script that Natali can use to run script using json from input folder to output folder

20160919-1645 - 20160919-1700: 15 minutes

    Get estimate_population to run on one node

# Tasks

## Important and easy

    Check for required columns like name
    Test when there are no demand points
    Test when there are demand points but no consumption
    Test that we only use most recent year if multiple years are given
    Replace geopy geocoding with error message about expected longitude latitude
    Add warning if peak_demand_in_kw is nan or zero
    Use global value if local value is nan

    Consider having different transformer tables for different locations
    Add acknowledgments to separate tools

    Fix oversizing system capacity
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
    Add instructions on how to set up the system on a new machine

    Report consumption for each node
    Add unelectrified option for zero consumption
    Report projected population count
    Report projected household count
    Need total inital and total recurring costs
    Need intermediate costs like diesel fuel cost per year
    Add sequence order in proposed network shapefiles for edge
    Add MV distance in proposed network shapefiles for edge
    Change use of maximum to total (e.g. connection count)
    Add household count and total and existing proposed grid length to summary
    Make it easy to clone scenarios
    Remove unnecessary files in output
    Fix command line overriding JSON
        Add test

    Let user download table
    Document ways that users can debug model
    Replace peak_demand with household and population info when clicking on node
    Explain that technologies chosen via networker not in coster #10
    Handle empty null values for number of people per household
    Update installation requirements

## Important and hard

    Consider separating line equipment cost vs installation cost
    Consider letting user specify installation and maintenance costs as percentages

    Write estimate_grid_mv_line_budget_in_meters to duplicate the beginning part of the script
    Convert tools into jupyter notebooks
    Add specification for model to jupyter notebooks

    Submit pull request for sequencer
    Separate Coster from Networker and Sequencer
    Separate Aggregator
    Write positive test

## Unimportant and easy

    Show overrided columns
    Let user download example table for each table
    Show simple map in addition to satellite map
    Adjust map colors to match old system
    Add legend to map

    Make notebook for each technology that only does modelling for that technology
    Add meta tool to explore demand threshold by varying household demand to change mvMax
    Consider tools that fill certain values based on administrative boundary
    Consider tools that fill certain values based on urban vs rural

    Cite "Total population, both sexes combined (thousands)" http://data.un.org/Data.aspx?d=PopDiv&f=variableID%3A12
    Cite "City population by sex, city and city type" http://data.un.org/Data.aspx?d=POP&f=tableCode:240
    Cite "Electric power consumption (kWh per capita)" http://data.worldbank.org/indicator/EG.USE.ELEC.KH.PC
    Cite "CIA World Factbook" https://www.cia.gov/library/publications/the-world-factbook/fields/2002.html
    Cite "GDP growth (annual %)" http://data.worldbank.org/indicator/NY.GDP.MKTP.KD.ZG
    Cite "Electric Sales, Revenue, and Average Price"
        http://www.eia.gov/electricity/sales_revenue_price/index.cfm
        http://www.eia.gov/electricity/sales_revenue_price/xls/table10.xls

    Update compute-discounted-cost
        Define loan_year in compute discounted cost
        Check whether different loan year affects breakeven time (whether we need to add loan year)

## Unimportant and hard

    Look into issues with live table override
        Fix table values on fly
    Show proposed network in different color or style from existing
    Consider letting user add row or column
    Clean up
        Move grow_exponentially into growth
        Make similar functions consistent with each other

    Consider accepting net present value vs consumption curve for energy source X
        Explain that net present value is a special case of discounted cash flow when there is spending in the first few years
    Look through past np errors
