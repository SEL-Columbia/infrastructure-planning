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

20160711-1700 - 20161026-1900: 108 days actual

# Objectives

1. + Fix bugs
2. + Update output files
3. _ Update executive summary by technology

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
        raw cost
        installation cost as percent of raw cost
        maintenance cost per year as percent of raw cost
        lifetime in years

    + Decide return values of prepare_system_cost

        system_capacity_in_kw or kva
        raw cost
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

20160926-1600 - 20160926-1630: 30 minutes

20160926-1700 - 20160926-1730: 30 minutes

20160926-1745 - 20160926-1815: 30 minutes

    + Rename prepare_actual_system_capacity to prepare_system_cost
    + Add raw cost to initial costs in prepare_component_cost_by_year

    _ lv_line_item_cost_per_meter
    _ lv_line_purchase_price_per_meter
    _ lv_line_purchase_cost_per_meter
    _ lv_line_product_cost_per_meter
    _ lv_line_material_cost_per_meter
    lv_line_raw_cost_per_meter
    _ lv_line_base_cost_per_meter
    _ lv_line_raw_material_cost_per_meter

    raw cost
    installation cost
    maintenance cost per year
    replacement cost per year

    + Update estimate_lv_line_cost to include raw cost and percents
    + Add lv_line_raw_cost_per_meter to parameters
    + Use lv_line_installation_cost_as_percent_of_raw_cost
        + Replace lv_line_installation_lm_cost_per_meter
    + Use lv_line_maintenance_cost_per_year_as_percent_of_raw_cost
        + Replace lv_line_maintenance_lm_cost_per_meter_per_year
    + Fix estimate_grid_lv_line_cost (fixed by estimate_lv_line_cost)
    + Fix estimate_diesel_mini_grid_lv_line_cost (fixed by estimate_lv_line_cost)
    + Fix estimate_solar_mini_grid_lv_line_cost (fixed by estimate_lv_line_cost)

20160927-1900 - 20160927-2000: 60 minutes

    + Update estimate_lv_connection_cost to include raw cost
    + Fix estimate_grid_lv_connection_cost (fixed by estimate_lv_connection_cost)
    + Fix estimate_diesel_mini_grid_lv_connection_cost (fixed by estimate_lv_connection_cost)
    + Fix estimate_solar_mini_grid_lv_connection_cost (fixed by estimate_lv_connection_cost)

20160927-2000 - 20160927-2100: 60 minutes

20160928-1400 - 20160928-1430: 30 minutes

    + Fix estimate_solar_mini_grid_battery_cost (fixed by estimate_battery_cost)
    + Fix estimate_solar_home_battery_cost (fixed by estimate_battery_cost)
    + Update estimate_battery_cost

20160928-1600 - 20160928-1630: 30 minutes

    + Update estimate_balance_cost
    + Fix estimate_solar_mini_grid_balance_cost (fixed by estimate_balance_cost)
    + Fix estimate_solar_home_balance_cost (fixed by estimate_balance_cost)
    + Make order of raw_cost calculations consistent

20160928-1730 - 20160928-1830: 60 minutes

    _ Rename _actual_system_capacty_in_kw to system_capacity_in_kw
    _ Rename _desired_system_capacty_in_kw to system_capacity_in_kw
    + Update estimate_grid_mv_line_cost_per_meter

20160928-1830 - 20160928-1900: 30 minutes

    + Fix estimate_grid_mv_transformer_cost (fixed by prepare_system_cost)

20160929-1030 - 20160929-1100: 30 minutes

    + Fix estimate_generator_cost (fixed by prepare_system_cost)
    + Fix estimate_solar_mini_grid_panel_cost (fixed by estimate_system_cost)
    + Fix estimate_solar_home_panel_cost (fixed by prepare_system_cost)
    + Update every use of prepare_component_cost_by_year for consistency

20160929-1630 - 20160929-1700: 30 minutes

We can round up by checking whether the first two differences are equal and if they are, then choosing the second one. This only works if the return order is consistent. Another alternative is to sort first by the difference and then sort by the capacity. Actually, I don't think we should round up. If the smaller generators are less efficient, then we should use the less efficient numbers in order to be conservative in our estimates.

20160930-1100 - 20160930-1130: 30 minutes

For each table where we have to do system sizing, we need to sort the table by capacity and make sure there are no duplicate capacity values.  We can either do this once at the beginning or do it when we have to size the system. However, we may need to use these tables again for other capacity dependent values. So it is safer to do it at the beginning.

Having all these normalizations and initializations scattered all over the place is too messy.  We'll look into how to consolidate and simplify this once we finish the most highly requested changes for this version.

    + Check that capacity values are unique for each table (there should be no duplicates)
    + Name initial variables
    + Draft table
    + Specify final variables
    + Draft system capacity algorithm
        + Have user specify generator capacity
        + Have user specify generator raw cost
        + Have user specify generator installation cost as fraction of raw cost
        + Have user specify maintenance cost per year as fraction of raw cost
        + Get desired system capacity
        _ Add system capacity safety factor
        + Compute raw cost per kw
        + Pick nearest generator capacity and use those costs per kw
        + Round actual capacity to integer
    _ Check that algorithm rounds up if it is equidistant

20160930-1600 - 20160930-1630: 30 minutes

We finished the new system sizing algorithm with a slight modification. Now we interpolate the values of raw_cost_per_unit_capacity and the other percents as well.

    + Fix oversizing system capacity
    + Update columns.txt with new names
    + Update parameter names in cc.ini
    + Update tables
        + Update example-diesel-generator-by-capacity.csv
        + Update example-grid-mv-transformer-by-capacity.csv
        + Update example-production-cost-by-year.csv
        + Update example-solar-panel-by-capacity.csv
    + Replace instances of _lm_
    + Update dummy.json
    + Update explanation text in tool.md
    + Consider separating line equipment cost vs installation cost
    + Consider letting user specify installation and maintenance costs as percentages

20160930-1800 - 20160930-1830: 30 minutes

It appears that the shapefile contains a MultiLineString.

20161003-1145 - 20161003-1245: 60 minutes

    + Find where the geometry coordinates are flipped
        Line 422
        Line 471
        Line 149
        Line 358
    + Draft code that will successfully flip the coordinates for the tanzania dataset

20161003-1700 - 20161003-1730: 30 minutes

    + Get model working on Tanzania dataset

20161004-1230 - 20161004-1300: 30 minutes

20161007-1045 - 20161007-1115: 30 minutes

20161007-1945 - 20161007-2015: 30 minutes

    _ Option 1: Store coordinate tuple as node id
    Option 2: Store wkb for each node and edge

Should we allow nodes to have identical coordinates?  If we don't allow it, then it will be much easier to save the shapefile.  Let me think.

If we allow duplicate coordinates, then we will need to attach a wkb for each node and edge.  The wkb for the edge will be constructed using the linestring.  Maybe that's not so hard either.

I think we should be able to accept a wkt for each node, then we get the centroid of that and make a linestring for each edge. If there is no wkt, then just get the latitude and longitude.

The main question is whether we should allow nodes to have identical coordinates.  We should err on the side of having simpler code.  Therefore I vote for having only unique coordinates.

    _ Make sure each node has unique coordinates

20161007-2200 - 20161007-2230: 30 minutes

Actually, we just explored the option of making sure each node has unique coordinates and we found that it would prevent allowing time series rows where there are multiple population years. It would also prevent the current usage of node_id as integer index, which we are currently assuming as returned by networker. Let's just go the wkb route.

We decided not to use networkx to save the shapefile because it doesn't save attributes.

20161012-1245 - 20161012-1300: 15 minutes

    + Record new feature requests

    _ adjust_for_loss_percents
    _ adjust_for_loss_fractions
    adjust_for_losses

20161014-2100 - 20161014-2130: 30 minutes

    + Review code

20161015-0000 - 20161015-0030: 30 minutes

    from infrastructure_planning.electricity.network import (assemble_total_mv_line_network, sequence_total_mv_line_network)
    _ from infrastructure_planning.electricity.cost.grid import (assemble_total_mv_line_network, sequence_total_mv_line_network)

20161015-0100 - 20161015-0130: 30 minutes

    + Separate Coster from Networker and Sequencer
    + Separate Aggregator

Last week, we discussed different ways to have the user override tables for different locations. The solution that Modi proposed is to have a cost multiplier for each technology.

    _ Consider having different transformer tables for different locations
    _ Look through past np errors
    _ Modify networker to accept line_length_adjustment_factor
    _ Consider using classes for individual part computations for inheritance
    _ Explain that net present value is a special case of discounted cash flow when there is spending in the first few years
    _ Add specification for model to jupyter notebooks
    _ Ignore installation cost percents for parts that don't need them
    + Clean task list

20161015-1300 - 20161015-1330: 30 minutes

    + Add unelectrified option for zero consumption
    _ Restore glossary
    _ Generate intermediate and yearly value files for debugging

20161024-1300 - 20161024-1330: 30 minutes

    + Check that everything still works
    + Check that dummy.json still works for Chris's system

For some reason, I'm getting an error.

Ok, it works now.

20161024-1400 - 20161024-1430: 30 minutes

    + Add BasicArgumentParser
    + Check that everything still works
    + Check tests

20161024-1430 - 20161024-1530: 60 minutes

I forgot how outputs work.

    _ A. Keep save_total_summary and make subfunctions

        save_values_by_location
        save_values_by_technology
        save_edge_summary
        save_node_summary

    B. Remove save_total_summary and use multiple functions

        save_total_values_by_location
        save_total_values_by_technology
        save_total_edge_summary
        save_total_node_summary

Let's pick option B so that we can have more independence with the requested parameters.

20161024-1545 - 20161024-1645: 60 minutes

    + Fix consumption threshold to be before grid
    + Set default consumption threshold to be 1 kwh/year

20161024-1645 - 20161024-1745: 60 minutes

    + Split save_total_summary

20161024-1930 - 20161024-2000: 30 minutes

    + Get full list of properties from computed node
    + Add list of parameters from tool.md
    + Add computed parameters
    + Make keys be separated by underscores in points.csv

20161024-2330 - 20161025-0000: 30 minutes

We're not going to be able to pass explicit node_ids the way the networker is currently written. So in case people want to screen by consumption, I say, just get rid of the ones you want to exclude and rerun the model.

    + Remove consumption_threshold_in_kwh_per_year

20161025-0030 - 20161025-0100: 30 minutes

    + Add solar_home_battery_kwh
    + Add projected population count
    + Add projected connection count

20161025-0730 - 20161025-0800: 30 minutes

    diesel_mini_grid_effective_hours_of_production_by_year
    _ diesel_mini_grid_final_effective_hours_of_production_per_year
    diesel_mini_grid_final_hours_of_production_per_year

    diesel_mini_grid_internal_distribution_cost_by_year
    _ diesel_mini_grid_electricity_internal_distribution_cost_by_year
    _ diesel_mini_grid_final_electricity_internal_distribution_cost_per_year
    diesel_mini_grid_final_internal_distribution_cost_per_year
    _ diesel_mini_grid_final_internal_electricity_distribution_cost_per_year

    diesel_mini_grid_electricity_production_cost_by_year
    diesel_mini_grid_final_electricity_production_cost_per_year
    _ diesel_mini_grid_final_production_cost_per_year

    diesel_mini_grid_electricity_production_in_kwh_by_year
    diesel_mini_grid_final_electricity_production_in_kwh_per_year
    _ diesel_mini_grid_final_production_in_kwh_per_year

    diesel_mini_grid_fuel_cost_by_year
    diesel_mini_grid_final_fuel_cost_per_year

20161025-0800 - 20161025-0830: 30 minutes

    + Add diesel_mini_grid_final_hours_of_production_per_year
    + Add diesel_mini_grid_final_fuel_cost_per_year
    + Add diesel_mini_grid_final_electricity_production_in_kwh_per_year
    + Add diesel_mini_grid_final_electricity_production_cost_per_year
    + Add diesel_mini_grid_final_internal_distribution_cost_per_year

    + Add grid_final_electricity_production_in_kwh_per_year
    + Add grid_final_electricity_production_cost_per_year
    + Add grid_final_internal_distribution_cost_per_year

    + Add solar_home_final_electricity_production_in_kwh_per_year
    + Add solar_home_final_electricity_production_cost_per_year
    + Add solar_home_final_internal_distribution_cost_per_year

    + Add solar_mini_grid_final_electricity_production_in_kwh_per_year
    + Add solar_mini_grid_final_electricity_production_cost_per_year
    + Add solar_mini_grid_final_internal_distribution_cost_per_year

20161025-1100 - 20161025-1200: 60 minutes

    + Add external_distribution_cost_per_year for consistency
    + Add intermediate costs like diesel fuel cost per year
    + Summarize some by year parameters using final
    + Exclude certain parameters
        _ selected_technologies
        _ population_by_year
        _ connection_count_by_year
        _ consumption_in_kwh_by_year
        _ diesel_mini_grid_effective_hours_of_production_by_year
        _ diesel_mini_grid_electricity_internal_distribution_cost_by_year
        _ diesel_mini_grid_electricity_production_cost_by_year
        _ diesel_mini_grid_electricity_production_in_kwh_by_year
        _ diesel_mini_grid_fuel_cost_by_year
        _ grid_electricity_internal_distribution_cost_by_year
        _ grid_electricity_production_cost_by_year
        _ grid_electricity_production_in_kwh_by_year
        _ solar_home_electricity_internal_distribution_cost_by_year
        _ solar_home_electricity_production_cost_by_year
        _ solar_home_electricity_production_in_kwh_by_year
        _ solar_mini_grid_electricity_internal_distribution_cost_by_year
        _ solar_mini_grid_electricity_production_cost_by_year
        _ solar_mini_grid_electricity_production_in_kwh_by_year

20161025-1200 - 20161025-1245: 45 minutes

    + Add total initial and total recurring costs
    + Add extra parameters

20161025-1245 - 20161025-1315: 30 minutes

    + Check why battery_storage_in_kwh is empty
    + Add miscellaneous parameters automatically
        + clinic_connection_count
        + clinic_consumption_in_kwh_per_year_per_clinic
        + household_connection_count
        + household_consumption_in_kwh_per_year_per_household
        + market_connection_count
        + market_consumption_in_kwh_per_year_per_market
        + school_connection_count
        + school_consumption_in_kwh_per_year_per_school
        + street_lamp_connection_count
        + street_lamp_consumption_in_kwh_per_year_per_street_lamp
    + Sort full list of properties
    + Generate points.csv

20161025-1430 - 20161025-1500: 30 minutes

    + Generate points.shp.zip
    + Add attributes to points.shp.zip
    + Check shapefile column name length limit
    + Include essential properties in shapefile

20161025-1630 - 20161025-1700: 30 minutes

    + Generate lines.csv
    + Generate lines-existing.shp
    + Generate lines-proposed.shp

20161025-1700 - 20161025-1800: 60 minutes

    + Add sequence order in proposed network shapefiles for edge
    + Add MV distance in proposed network shapefiles for edge
    + Remove edges* intermediate files
    + Remove grid_mv_line table
    + Remove nodes* intermediate files
    + Remove unnecessary files in output
    + Clean up output folder
        + result.cfg
        + run.sh
        stdout.log
        stderr.log
        _ infrastructure-graph.pkl (too big)
        + infrastructure-map.csv
        + arguments/arguments.csv
        + arguments/arguments.json
        + arguments/connection-type-table.csv
        + arguments/demand-point-table.csv
        + arguments/diesel-mini-grid-generator-table.csv
        + arguments/grid-mv-line-geotable.csv
        + arguments/grid-mv-transformer-table.csv
        + arguments/selected-technologies-text.txt
        + arguments/solar-home-panel-table.csv
        + arguments/solar-mini-grid-panel-table.csv
        + properties/points.csv
        + properties/points.shp.zip
        + properties/lines.csv
        + properties/lines-existing.shp.zip
        + properties/lines-proposed.shp.zip
        + reports/example-by-technology.csv
        + reports/report-by-location.csv
        + reports/summary-by-grid-mv-line.csv
        + reports/summary-by-location.csv
        + reports/summary-by-technology.csv

20161025-1800 - 20161025-1830: 30 minutes

    + Add acknowledgments to separate tools in tool.md

20161026-1330 - 20161026-1400: 30 minutes

    _ initial fixed
    _ recurring fixed
    _ recurring variable

    _ initial
    _ fixed recurring
    _ variable recurring

    _ construction
    _ distribution
    _ production

    _ initial distribution
    _ recurring distribution
    _ production

    grid_initial_cost
    grid_fixed_cost_per_year
    grid_variable_cost_per_year
    _ grid_volatile_cost_per_year

    grid_initial_cost
    grid_recurring_fixed_cost_per_year
    grid_recurring_variable_cost_per_year

    _ grid_capital_cost
    _ grid_recurring_fixed_cost_per_year
    _ grid_recurring_variable_cost_per_year

20161026-1430 - 20161026-1500: 30 minutes

    grid_internal_initial_cost
    grid_internal_recurring_fixed_cost_per_year
    grid_internal_recurring_variable_cost_per_year

    grid_external_initial_cost
    grid_external_recurring_fixed_cost_per_year
    grid_external_recurring_variable_cost_per_year

    grid_local_initial_cost
    grid_local_recurring_fixed_cost_per_year
    grid_local_recurring_variable_cost_per_year

    initial = raw + installation
    fixed = maintenance + replacement
    variable = get_final_value(electricity_production_cost_by_year)

    _ grid_mv_line_cost_by_year_per_meter
    grid_mv_line_cost_per_meter_by_year

    _ grid_mv_line_final_cost_per_year_per_meter
    grid_mv_line_final_cost_per_meter_per_year

    + Compute grid_mv_line_raw_cost

20161026-1715 - 20161026-1745: 30 minutes

Should we include grid_mv_line_adjusted_budget_in_meters for nodes that are not connected to the grid?  I don't think so.

    + Compute internal and external summary costs

20161026-1845 - 20161026-1900: 15 minutes

    + Check that everything works
