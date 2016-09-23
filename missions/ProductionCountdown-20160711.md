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

    + Get estimate_population to run

20160919-1915 - 20160919-1945: 30 minutes

    + Make sure script runs with defaults
    + Open costs.csv
    + See whether we compute the equivalent of projected nodal discounted demand

It looks like the reason that I do not compute projected nodal discounted demand is because we use the time series consumption_in_kwh_by_year instead. The best way to illustrate this is using a jupyter notebook traced along a single node.

We could compute the discounted consumption for illustration purposes.

    _ Report consumption for each node

20160920-1045 - 20160920-1100: 15 minutes

After looking at the different uses of maximum and total, it is important to distinguish maximum when we are taking the maximum of a time series.

    _ Change use of maximum to total (e.g. connection count)

An alternative is to use final instead of maximum. This will still capture the concept that the production per year reported is one of many.

    maximum_connection_count
    maximum_consumption_in_kwh_per_year
    maximum_consumption_during_peak_hours_in_kwh_per_year
    maximum_production_in_kwh_per_year

Currently we are using the prefix maximum.

    total_connection_count
    total_consumption_in_kwh_per_year
    total_consumption_during_peak_hours_in_kwh_per_year
    total_production_in_kwh_per_year

If we change the prefix to total, it gives the mistaken connotation that the value is constant each year.

    final_connection_count
    final_consumption_in_kwh_per_year
    final_consumption_during_peak_hours_in_kwh_per_year
    final_production_in_kwh_per_year

If we use final, that opens the possibility of using something other than the maximum and it also captures the sense that the value can change over many years. Let's use final. The only thing is that it is inconsistent with how total is used in the relative values.

    _ consumption_during_peak_hours_as_percent_of_total_consumption
    _ grid_system_loss_as_percent_of_total_production
    _ diesel_mini_grid_system_loss_as_percent_of_total_production
    _ solar_home_system_loss_as_percent_of_total_production
    _ solar_mini_grid_system_loss_as_percent_of_total_production

Above is how it is currently. It makes sense, but using total is inconsistent with maximum_connection_count or final_connection_count.

    _ consumption_during_peak_hours_as_percent_of_maximum_consumption
    _ grid_system_loss_as_percent_of_maximum_production
    _ diesel_mini_grid_system_loss_as_percent_of_maximum_production
    _ solar_home_system_loss_as_percent_of_maximum_production
    _ solar_mini_grid_system_loss_as_percent_of_maximum_production

The above gives the false impression that the percent is only relative to the maximum, which it is not.

    consumption_during_peak_hours_as_percent_of_consumption
    grid_system_loss_as_percent_of_production
    diesel_mini_grid_system_loss_as_percent_of_production
    solar_home_system_loss_as_percent_of_production
    solar_mini_grid_system_loss_as_percent_of_production

Not having any qualifier can be confusing, but not really.

    _ consumption_during_peak_hours_as_percent_of_final_consumption
    _ grid_system_loss_as_percent_of_final_production
    _ diesel_mini_grid_system_loss_as_percent_of_final_production
    _ solar_home_system_loss_as_percent_of_final_production
    _ solar_mini_grid_system_loss_as_percent_of_final_production

20160921-1315 - 20160920-1345: 30 minutes

I think the decisions are to use final_connection_count and consumption_during_peak_hours_as_percent_of_consumption.

    + Rename maximum_connection_count to final_connection_count
    + Rename maximum_consumption_in_kwh_per_year to final_consumption_in_kwh_per_year
    + Rename maximum_consumption_during_peak_hours_in_kwh_per_year to final_consumption_during_peak_hours_in_kwh_per_year
    + Rename maximum_production_in_kwh_per_year to final_production_in_kwh_per_year

    _ Rename consumption_during_peak_hours_as_percent_of_total_consumption to consumption_during_peak_hours_as_percent_of_consumption
    _ Rename grid_system_loss_as_percent_of_total_production to grid_system_loss_as_percent_of_production
    _ Rename diesel_mini_grid_system_loss_as_percent_of_total_production to diesel_mini_grid_system_loss_as_percent_of_production
    _ Rename solar_home_system_loss_as_percent_of_total_production to solar_home_system_loss_as_percent_of_production
    _ Rename solar_mini_grid_system_loss_as_percent_of_total_production to solar_mini_grid_system_loss_as_percent_of_production

Actually, consumption_during_peak_hours_as_percent_of_total_consumption is clearer than consumption_during_peak_hours_as_percent_of_consumption, which seems recursive and is confusing. We'll keep the nomenclature for the percentage parameters.

20160920-1400 - 20160920-1430: 30 minutes

    grid_internal_discounted_cost
    grid_external_discounted_cost
    = grid_local_discounted_cost
    _ grid_nodal_discounted_cost
    _ grid_system_discounted_cost
    _ grid_allocated_discounted_cost
    _ grid_total_discounted_cost

    grid_local_levelized_cost_per_kwh_produced
    grid_local_levelized_cost_per_kwh_consumed

    _ grid_local_cost_per_kwh_produced
    _ grid_local_cost_per_kwh_consumed
    _ grid_local_cost_per_produced_kwh
    _ grid_local_cost_per_consumed_kwh

20160920-1430 - 20160920-1500: 30 minutes

The code is in infrastructure_planning/electricity/cost/__init__.py on line 93. I would need to compute discounted_consumption_in_kwh.

    + Pinpoint where levelized cost is being computed

    _ Option 1: Compute discounted_consumption_in_kwh in consumption module
    Option 2: Add second function to MAIN_FUNCTIONS that computes discounted consumption
    _ Option 3: Compute discounted_consumption_in_kwh in prepare_internal_cost

The issue with option 3 is that the computation will duplicate for each technology, not a big deal, but not optimal.

The issue with option 1 is that we are introducing financial parameters that are not stricly necessary to estimate consumption.

However, we're also going to need discounted consumption again in the global computation, so that eliminates option 3.

Then we choose between option 1 and option 2. We choose option 2.

    _ estimate_summarized_consumption
    _ estimate_discounted_consumption
    _ estimate_consumption_statistics
    _ estimate_consumption_features
    estimate_consumption_profile
    _ estimate_consumption_portrait
    _ estimate_consumption_sketch
    _ condense_consumption_profile
    _ discount_consumption
    _ discount_future_consumption

    + Define estimate_consumption_profile
    + Update computation for levelized_cost in internal cost
    + Update computation for levelized_cost in total cost

20160920-1815 - 20160920-1845: 30 minutes

20160921-1800 - 20160921-1830: 30 minutes

    class ExpectedPositive
    _ class ExpectedNonZero
    _ class ExpectedGreaterThanZero
    _ class MustBeGreaterThanZero
    _ class NeedGreaterThanZero
    _ class BeGreaterThanZero
    _ class NotGreaterThanZero

    + Replace division by float(x) with divide_safely
    + Check divide_safely calls to accept cases where denominator could legitimately be blank
    + Raise ExpectedPositive instead of InvalidData

20160922-1115 - 20160922-1145: 30 minutes

    grid_local_levelized_cost_per_kwh_consumed
    _ grid_total_levelized_cost
    _ grid_local_cost_per_kwh_consumed

20160922-1730 - 20160922-1800: 30 minutes

    + Convert compute-levelized-cost-per-kwh-consumed into notebook

    + Rename grid_total_levelized_cost to grid_local_levelized_cost_per_kwh_consumed
    + Rename diesel_mini_grid_total_levelized_cost to diesel_mini_grid_local_levelized_cost_per_kwh_consumed
    + Rename solar_home_total_levelized_cost to solar_home_local_levelized_cost_per_kwh_consumed
    + Rename solar_mini_grid_total_levelized_cost to solar_mini_grid_local_levelized_cost_per_kwh_consumed

    + Rename grid_total_discounted_cost to grid_local_discounted_cost
    + Rename diesel_mini_grid_total_discounted_cost to diesel_mini_grid_local_discounted_cost
    + Rename solar_home_total_discounted_cost to solar_home_local_discounted_cost
    + Rename solar_mini_grid_total_discounted_cost to solar_mini_grid_local_discounted_cost

20160922-1930 - 20160922-1945: 15 minutes

It looks like we need to aggregate consumption grouped by technology. Okay we fixed that. We should really add some numeric spot checks.

    + Compute cost per kwh delivered to consumer instead of cost per kwh produced

20160923-1130 - 20160923-1200: 30 minutes

    + Look at where exactly we are sizing system capacity
    + Review how prepare_component_cost_by_year works
    + Review the need for get_by_prefix

The issue is that there will be material costs during maintenance and replacement.

    purchase price
    _ purchase cost
    _ raw cost
    _ machine cost
    _ material cost (there could be material costs during maintenance and replacement)
    _ sale cost
    _ initial material cost
    _ installation price
    installation cost
    maintenance cost
    replacement cost

The expression "purchase price" seems to be standard, but it is inconsistent with the use of the word cost. Perhaps we can use a synonym to purchase.

I think what is instructive is [this article](http://www.investopedia.com/ask/answers/101314/what-difference-between-cost-and-price.asp) that says that price is the amount a business pays for the raw product and costs are the expenses incurred in bringing the product to market. In that case, our use of purchase price and installation cost is correct from the perspective of the utility, which is purchasing a generator and incurring the cost of installing and maintaining it.

    + Decide nomenclature

20160923-1230 - 20160923-1300: 30 minutes

Here are the anticipated changes:

    _ estimate_system_cost
    _ estimate_system_costs
    _ prepare_system_costs
    purchase price
    installation cost
    maintenance cost
    replacement cost

    + Think through anticipated changes
    + Decide columns in table

        capacity in kw or kva
        purchase price
        installation cost as percent of purchase price
        maintenance cost per year as percent of purchase price
        lifetime in years

    + Decide return values of prepare_system_cost

        system_capacity_in_kw or kva
        purchase price
        installation cost
        maintenance cost per year
        replacement cost per year

    + Record anticipated changes

20160923-1500 - 20160923-1530: 30 minutes

20160923-1600 - 20160923-1630: 30 minutes

    _ Get complete diff between the two versions
    _ Select which things we need to include

I think this is too complicated.

    + Send sequencer pull request
    + Submit pull request for sequencer



    Draft system capacity algorithm



        Add purchase price to initial costs in prepare_component_cost_by_year
        Rename prepare_actual_system_capacity to prepare_system_cost
        Update estimate_lv_line_cost to include purchase price
        Update estimate_lv_connection_cost to include purchase price
        Update estimate_grid_mv_line_cost_per_meter
        Update estimate_diesel_mini_grid_fuel_cost
        Update estimate_battery_cost
        Update estimate_balance_cost
        Update every use of prepare_component_cost_by_year for consistency
            purchase price
            installation cost
            maintenance cost per year
            replacement cost per year

            estimate_grid_mv_transformer_cost (fixed by prepare_system_cost)
            estimate_grid_lv_line_cost (fixed by estimate_lv_line_cost)
            estimate_grid_lv_connection_cost (fixed by estimate_lv_connection_cost)
            estimate_grid_mv_line_cost_per_meter
            estimate_generator_cost (fixed by prepare_system_cost)
            estimate_diesel_mini_grid_lv_line_cost (fixed by estimate_lv_line_cost)
            estimate_diesel_mini_grid_lv_connection_cost (fixed by estimate_lv_connection_cost)
            estimate_solar_mini_grid_panel_cost (fixed by estimate_system_cost)
            estimate_solar_mini_grid_battery_cost (fixed by estimate_battery_cost)
            estimate_solar_mini_grid_balance_cost (fixed by estimate_balance_cost)
            estimate_solar_mini_grid_lv_line_cost (fixed by estimate_lv_line_cost)
            estimate_solar_mini_grid_lv_connection_cost (fixed by estimate_lv_connection_cost)
            estimate_solar_home_panel_cost (fixed by prepare_system_cost)
            estimate_solar_home_battery_cost (fixed by estimate_battery_cost)
            estimate_solar_home_balance_cost (fixed by estimate_balance_cost)
        Update columns.txt with new names
        Update parameter names in cc.ini

    Name initial variables
    Draft table
    Specify final variables

    Fix oversizing system capacity
        Update system size algorithm
            Have user specify generator capacity
            Have user specify generator purchase price
            Have user specify generator installation cost as fraction of purchase price
            Have user specify maintenance cost per year as fraction of purchase price
            Get desired system capacity
            _ Add system capacity safety factor
            Compute purchase price per kw
            Pick nearest generator capacity and use those prices per kw
            Round actual capacity to integer

# Tasks

## Important and easy

    Add sequence order in proposed network shapefiles for edge
    Add MV distance in proposed network shapefiles for edge

    Test when there are demand points but no consumption
    Test when there are no demand points
    Add unelectrified option for zero consumption

    Report projected population count
    Report projected connection count
    Need total initial and total recurring costs
    Need intermediate costs like diesel fuel cost per year

    Draft jupyter notebook that starts from the population of a single node

    Check for required columns like name
    Replace geopy geocoding with error message about expected longitude latitude
    Add warning if peak_demand_in_kw is nan or zero
    Use global value if local value is nan
    Test that we only use most recent year if multiple years are given

    Consider having different transformer tables for different locations
    Add acknowledgments to separate tools

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
        /properties/summary.csv
        /interface/map.csv
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

    Separate Coster from Networker and Sequencer
    Separate Aggregator
        Look at label for node and compute metrics by cluster
    Write positive test

## Unimportant and easy

    Consider having fuel efficiency vary by generator

    Make sure that capacities in tables are greater than zero
    Make sure that lifetimes in tables are greater than zero

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

    Modify networker to accept line_length_adjustment_factor
