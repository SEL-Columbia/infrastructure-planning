# Vision
Ensure a successful transition to the new infrastructure-planning system.

# Mission
Derive default values from Leona in Senegal and Kaduna in Nigeria.

# Owner
Roy Hyunjin Han

# Context
We would like to make it easy for Naichen, Shaky, Edwin to start testing the new system.

# Timeframe
20160613-1100 - 20160617-1600: 4 days estimated

# Objectives
1. Derive default values for Leona in Senegal.
2. Derive default values for Kaduna in Nigeria.
3. Draft some notes on how to derive certain values.

# Log
20160613-1115 - 20160613-1215

Let's first fill the Senegal default values.

I'm having a little trouble deriving consumption_in_kwh_per_year_per_connection. We can estimate a default value for this by running the Leona dataset in the original NetworkPlanner with the old, non-zeroed defaults, then summing consumption and counting connections and dividing.

    Household unit demand per household per year
        100 kWh / year
    Productive unit demand per household per year
        19.5 kWh / year
    Commercial facility unit demand per commercial facility per year
        250 kWh / year
    Education facility unit demand per education facility per year
        1200 kWh / year
    Health facility unit demand per health facility per year
        1000 kWh / year
    Public lighting facility unit demand per public lighting facility per year
        102 kWh / year

Okay, we ran the old NetworkPlanner mvMax4 model on the old Leona dataset using the defaults above, which we took from http://networkplanner.modilabs.org/docs/metric-mvMax4.html#mvmax4-demand-householdunitdemandperhouseholdperyear.

Now let's sum the values that interest us. In the old model, we mistakenly used "demand" instead of "consumption" to mean kWh.

    Demand > Projected nodal demand per year
        1152940.46722064 kWh / year

From the individual counts, we get 3406.2351435363 total connections.

    Demand (social infrastructure) > Projected commercial facility count
        20.6972838976 commercial facilities
    Demand (social infrastructure) > Projected education facility count
        16.3928104733 education facilities
    Demand (social infrastructure) > Projected health facility count
        24.8276592866 health facilities
    Demand (social infrastructure) > Projected public lighting facility count
        17.3173898788 public lighting facilities
    Demographics > Projected household count
        3327 households

From the grid installation cost, we get 3406.235143537246 total connections.

    System (grid) > Installation cost per connection
        130 dollars
    System (grid) > Installation cost
        442810.568659842 dollars

That means that our "consumption_in_kwh_per_year_per_connection" is 338.47941161905663 kWh / year. We'll round that to 339 kWh / year.

I might need a step by step document that shows how to convert parameters from the old NetworkPlanner to the new infrastructure-planning system.

20160617-1300 - 20160617-1600: 3 hours

Let's first finishing implementing estimate_consumption_from_connection_type. Then we'll finish with the JSON parameters for Senegal and Nigeria so that the system is ready for testing by Naichen, Shaky, Edwin and then we'll call it a day.

It looks like I had the original estimate_consumption return arrays of values by year.

    connection_count_by_year
    consumption_in_kwh_by_year

I think this was because I wanted some downstream values to compute things year by year, such as perhaps the recurring cost of low voltage line. However, for various reasons we decided to use only the maximum value. At the same time, I would like to preserve the yearly values just in case someone wants to use these later.

Let's aim to finish estimate_consumption_from_connection_type by 2pm. Then I'll have two hours to finish the JSON parameters

    Option 1: Identify connection type components then add them together.
    _ Option 2: Convert everything into yearly values then add them together.

20160617-1530

We finished estimate_consumption_from_connection_type.

20160706-1630 - 20160706-1745

Let's start with name.

# Tasks

    Write script to convert old parameters to new parameters
		average_distance_between_buildings_in_meters
		consumption_during_peak_hours_as_percent_of_total_consumption
		diesel_mini_grid_electricity_discounted_production_in_kwh
		diesel_mini_grid_external_discounted_cost
		diesel_mini_grid_fuel_cost_per_liter
		diesel_mini_grid_generator_actual_system_capacity_in_kw
		diesel_mini_grid_generator_desired_system_capacity_in_kw
		diesel_mini_grid_generator_fuel_liters_consumed_per_kwh
		diesel_mini_grid_generator_installation_lm_cost
		diesel_mini_grid_generator_maintenance_lm_cost_per_year
		diesel_mini_grid_generator_minimum_hours_of_production_per_year
		diesel_mini_grid_generator_replacement_lm_cost_per_year
		diesel_mini_grid_generator_selected_capacity_in_kw
		diesel_mini_grid_generator_selected_count
		diesel_mini_grid_internal_discounted_cost
		diesel_mini_grid_internal_levelized_cost
		diesel_mini_grid_lv_connection_installation_lm_cost
		diesel_mini_grid_lv_connection_installation_lm_cost_per_connection
		diesel_mini_grid_lv_connection_lifetime_in_years
		diesel_mini_grid_lv_connection_maintenance_lm_cost_per_connection_per_year
		diesel_mini_grid_lv_connection_maintenance_lm_cost_per_year
		diesel_mini_grid_lv_connection_replacement_lm_cost_per_year
		diesel_mini_grid_lv_line_installation_lm_cost
		diesel_mini_grid_lv_line_installation_lm_cost_per_meter
		diesel_mini_grid_lv_line_lifetime_in_years
		diesel_mini_grid_lv_line_maintenance_lm_cost_per_meter_per_year
		diesel_mini_grid_lv_line_maintenance_lm_cost_per_year
		diesel_mini_grid_lv_line_replacement_lm_cost_per_year
		diesel_mini_grid_system_loss_as_percent_of_total_production
		diesel_mini_grid_total_discounted_cost
		diesel_mini_grid_total_levelized_cost
		discount_rate_as_percent_of_cash_flow_per_year
		financing_year
		grid_electricity_discounted_production_in_kwh
		grid_electricity_production_cost_per_kwh
		grid_external_discounted_cost
		grid_internal_discounted_cost
		grid_internal_levelized_cost
		grid_lv_connection_installation_lm_cost
		grid_lv_connection_installation_lm_cost_per_connection
		grid_lv_connection_lifetime_in_years
		grid_lv_connection_maintenance_lm_cost_per_connection_per_year
		grid_lv_connection_maintenance_lm_cost_per_year
		grid_lv_connection_replacement_lm_cost_per_year
		grid_lv_line_installation_lm_cost
		grid_lv_line_installation_lm_cost_per_meter
		grid_lv_line_lifetime_in_years
		grid_lv_line_maintenance_lm_cost_per_meter_per_year
		grid_lv_line_maintenance_lm_cost_per_year
		grid_lv_line_replacement_lm_cost_per_year
		grid_mv_line_adjusted_budget
		grid_mv_line_adjusted_length_in_meters
		grid_mv_line_discounted_cost_per_meter
		grid_mv_line_installation_lm_cost_per_meter
		grid_mv_line_installation_lm_cost_per_meter
		grid_mv_line_lifetime_in_years
		grid_mv_line_maintenance_lm_cost_per_meter_per_year
		grid_mv_line_maintenance_lm_cost_per_meter_per_year
		grid_mv_line_replacement_lm_cost_per_meter_per_year
		grid_mv_network_minimum_point_count
		grid_mv_transformer_actual_system_capacity_in_kva
		grid_mv_transformer_desired_system_capacity_in_kva
		grid_mv_transformer_installation_lm_cost
		grid_mv_transformer_load_power_factor
		grid_mv_transformer_maintenance_lm_cost_per_year
		grid_mv_transformer_replacement_lm_cost_per_year
		grid_mv_transformer_selected_capacity_in_kva
		grid_mv_transformer_selected_count
		grid_system_loss_as_percent_of_total_production
		grid_total_discounted_cost
		grid_total_levelized_cost
		json
		latitude
		line_length_adjustment_factor
		longitude
		maximum_connection_count
		maximum_consumption_in_kwh_per_year
		number_of_people_per_household
		order
		peak_demand_in_kw
		peak_hours_of_consumption_per_year
		peak_hours_of_sun_per_year
		population
		population_growth_as_percent_of_population_per_year
		population_year
		proposed_cost_per_connection
		proposed_technology
		solar_home_balance_installation_lm_cost
		solar_home_balance_installation_lm_cost_per_panel_kw
		solar_home_balance_lifetime_in_years
		solar_home_balance_maintenance_lm_cost_per_panel_kw_per_year
		solar_home_balance_maintenance_lm_cost_per_year
		solar_home_balance_replacement_lm_cost_per_year
		solar_home_battery_installation_lm_cost
		solar_home_battery_installation_lm_cost_per_battery_kwh
		solar_home_battery_kwh_per_panel_kw
		solar_home_battery_lifetime_in_years
		solar_home_battery_maintenance_lm_cost_per_kwh_per_year
		solar_home_battery_maintenance_lm_cost_per_year
		solar_home_battery_replacement_lm_cost_per_year
		solar_home_electricity_discounted_production_in_kwh
		solar_home_external_discounted_cost
		solar_home_internal_discounted_cost
		solar_home_internal_levelized_cost
		solar_home_panel_actual_system_capacity_in_kw
		solar_home_panel_desired_system_capacity_in_kw
		solar_home_panel_installation_lm_cost
		solar_home_panel_maintenance_lm_cost_per_year
		solar_home_panel_replacement_lm_cost_per_year
		solar_home_panel_selected_capacity_in_kw
		solar_home_panel_selected_count
		solar_home_system_loss_as_percent_of_total_production
		solar_home_total_discounted_cost
		solar_home_total_levelized_cost
		solar_mini_grid_balance_installation_lm_cost
		solar_mini_grid_balance_installation_lm_cost_per_panel_kw
		solar_mini_grid_balance_lifetime_in_years
		solar_mini_grid_balance_maintenance_lm_cost_per_panel_kw_per_year
		solar_mini_grid_balance_maintenance_lm_cost_per_year
		solar_mini_grid_balance_replacement_lm_cost_per_year
		solar_mini_grid_battery_installation_lm_cost
		solar_mini_grid_battery_installation_lm_cost_per_battery_kwh
		solar_mini_grid_battery_kwh_per_panel_kw
		solar_mini_grid_battery_lifetime_in_years
		solar_mini_grid_battery_maintenance_lm_cost_per_kwh_per_year
		solar_mini_grid_battery_maintenance_lm_cost_per_year
		solar_mini_grid_battery_replacement_lm_cost_per_year
		solar_mini_grid_electricity_discounted_production_in_kwh
		solar_mini_grid_external_discounted_cost
		solar_mini_grid_internal_discounted_cost
		solar_mini_grid_internal_levelized_cost
		solar_mini_grid_lv_connection_installation_lm_cost
		solar_mini_grid_lv_connection_installation_lm_cost_per_connection
		solar_mini_grid_lv_connection_lifetime_in_years
		solar_mini_grid_lv_connection_maintenance_lm_cost_per_connection_per_year
		solar_mini_grid_lv_connection_maintenance_lm_cost_per_year
		solar_mini_grid_lv_connection_replacement_lm_cost_per_year
		solar_mini_grid_lv_line_installation_lm_cost
		solar_mini_grid_lv_line_installation_lm_cost_per_meter
		solar_mini_grid_lv_line_lifetime_in_years
		solar_mini_grid_lv_line_maintenance_lm_cost_per_meter_per_year
		solar_mini_grid_lv_line_maintenance_lm_cost_per_year
		solar_mini_grid_lv_line_replacement_lm_cost_per_year
		solar_mini_grid_panel_actual_system_capacity_in_kw
		solar_mini_grid_panel_desired_system_capacity_in_kw
		solar_mini_grid_panel_installation_lm_cost
		solar_mini_grid_panel_maintenance_lm_cost_per_year
		solar_mini_grid_panel_replacement_lm_cost_per_year
		solar_mini_grid_panel_selected_capacity_in_kw
		solar_mini_grid_panel_selected_count
		solar_mini_grid_system_loss_as_percent_of_total_production
		solar_mini_grid_total_discounted_cost
		solar_mini_grid_total_levelized_cost
		time_horizon_in_years
    Draft JSON file from Senegal defaults
    Draft JSON file from Nigeria defaults
    Revise parameter defaults to fit Nigeria defaults
