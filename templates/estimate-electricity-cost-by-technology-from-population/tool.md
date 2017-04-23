# Estimate Electricity Cost by Technology from Population

- [Version 3 (2016)](https://github.com/sel-columbia/infrastructure-planning)
    - Principal Investigator: Vijay Modi
    - Project Manager: Edwin Adkins
    - Econometric Analyst: Naichen Zhao
    - Spatial Analyst: Shaky Sherpa
    - Software Engineers: Chris Natali, Roy Hyunjin Han, Viktor Roytman
- Version 2 (2013)
    - Principal Investigator: Vijay Modi
    - Project Manager: Edwin Adkins
    - Operations Research Analyst: Ayse Selin Kocaman
    - Econometric Analyst: Jonathan Carbajal
    - Spatial Analyst: Shaky Sherpa
    - Software Engineers: Chris Natali, Brandon Ogle
- Version 1 (2010)
    - Principal Investigator: Vijay Modi
    - Project Managers: Edwin Adkins, Alex Hofmann, Matt Berg
    - Project Advisors: Jonah Bossewitch, Rob Garfield
    - Operations Research Analysts: Alex Zvoleff, Ayse Selin Kocaman
    - Econometric Analysts: Sahil Shah, Aly Sanoh
    - Spatial Analyst: Susan Kum
    - Graphic Designers: Andrew Doro, Zarina Mustapha
    - Software Engineers: Roy Hyunjin Han, Po-Han Freeza Huang, Anders Pearson, Ethan Jucovy
- Version 0 (2008)
    - Principal Investigator: Vijay Modi
    - Doctoral Researchers: Lily Parshall, Aly Sanoh
    - Econometric Analyst: Arnaud Algrin
    - Spatial Analyst: Dana Pillai
    - Software Engineer: Shashank Mohan

Each technology has initial installation costs and recurring production, maintenance and replacement costs.

Mini-grid technologies include a central production facility and a low-voltage distribution network.

{selected_technologies_text}




## Finance
The amount of money needed to fund an infrastructure project includes both initial and recurring costs. The initial costs are paid upfront and the recurring costs are paid later.

The net present value or discounted cost of an infrastructure project assumes that you will invest the money that you are not using now. For example, if a $110k project will start next year and if you are confident that you will earn at least 10% through investments, then you can request a loan for $100k one year in advance.

{financing_year}
{time_horizon_in_years}
{discount_rate_as_percent_of_cash_flow_per_year}




## Demography
Assume that population grows at a fixed rate each year. If the population is 100 and the growth rate is 10%, then the population will be 110 after the first year and 121 after the second year.

{demand_point_table: demand points}

To override a computed value for specific demand points, upload a CSV with an additional column. The column name should match the name of the variable that you are overriding. Variable names are available in the *glossary.csv* file that is generated after running this tool.

Note that if you leave a blank entry in a local override column, then the system will not override the value for that demand point.

{population_year}
{population_growth_as_percent_of_population_per_year}




## Geography

{line_length_adjustment_factor}

The length of line used to connect two locations is often greater than the distance between the two locations.

{average_distance_between_buildings_in_meters}
{peak_hours_of_sun_per_year}




## Consumption
Assume that consumption is fixed per capita. Estimate consumption based on the projected population.

{connection_type_table: connection types}

To override connection count and consumption by connection type for specific demand points, please use the following column name format in the *Demand Point Table* above:

- xyz_connection_count
- xyz_consumption_in_kwh_per_year_per_xyz

For example, the following column names in the *Demand Point Table* will override household connection count and consumption:

- household_connection_count
- household_consumption_in_kwh_per_year_per_household

By default, *household_connection_count* is relative to the size of the population for each year.  Overriding *household_connection_count* will result in *household_connection_count* being **constant year over year**.

The following column names in the *Demand Point Table* will override market count and consumption, but only if *market* exists as a connection type in the *Connection Type Table* below:

- market_connection_count
- market_consumption_in_kwh_per_year_per_market

{number_of_people_per_household}
{consumption_during_peak_hours_as_percent_of_total_consumption}
{peak_hours_of_consumption_per_year}




## Technology: Grid
A remote source produces electricity that is distributed to consumers.

* Recurring Production Cost
    * Assume that we must produce more than what we consume because of distribution losses.
    * Production cost is the loss-adjusted local consumption in kWh multiplied by the electricity production cost per kWh.

{grid_electricity_production_cost_per_kwh}
{grid_system_loss_as_percent_of_total_production}


### Grid Medium Voltage Line
Medium voltage lines carry electricity over large distances.

* Initial Raw Cost is proportional to the number of meters of medium voltage line in the network.
* Initial Installation Cost is proportional to the Raw Cost.
* Recurring Maintenance Cost is proportional to the Raw Cost.
* Recurring Replacement Cost is the Initial Cost divided by lifetime.

{grid_mv_network_minimum_point_count}
{grid_mv_line_geotable: grid mv lines (existing)}
{grid_mv_line_raw_cost_per_meter}
{grid_mv_line_installation_cost_as_percent_of_raw_cost}
{grid_mv_line_maintenance_cost_per_year_as_percent_of_raw_cost}
{grid_mv_line_lifetime_in_years}


### Grid Medium Voltage Transformer
Medium voltage transformers convert medium voltage to low voltage.

* Initial Raw Cost
    * The cost of a transformer depends on its capacity, which is how much electricity it can deliver. Transformer capacity is listed in kVA. If the power factor of the load is 0.85, then the number of kWh delivered is kVA * 0.85.
    * Size transformer capacity based on estimated peak demand. Estimate the amount of loss-adjusted consumption that is happening during peak hours. Divide the loss-adjusted consumption by the number of peak hours per year to estimate peak demand.
    * Find the two transformers that are closest to the desired capacity.
    * Compute the raw cost per unit capacity for each of the two selected transformers.
    * Interpolate the raw cost per unit capacity relative to the desired capacity.
    * Multiply the raw cost per unit capacity by the desired capacity.
* Initial Installation Cost is proportional to the Raw Cost.
* Recurring Maintenance Cost is proportional to the Raw Cost.
* Recurring Replacement Cost is the Initial Cost divided by lifetime.

{grid_mv_transformer_load_power_factor}
{grid_mv_transformer_table: grid mv transformers}


### Grid Low Voltage Line
Low voltage lines distribute electricity over small distances.

* Initial Raw Cost
    * Multiply the raw cost of low voltage line per meter by the estimated number of meters of low voltage line.
    * The number of meters of LV line is the number of connections multiplied by the average distance between buildings.
* Initial Installation Cost is proportional to the Raw Cost.
* Recurring Maintenance Cost is proportional to the Raw Cost.
* Recurring Replacement Cost is the Initial Cost divided by lifetime.

{grid_lv_line_raw_cost_per_meter}
{grid_lv_line_installation_cost_as_percent_of_raw_cost}
{grid_lv_line_maintenance_cost_per_year_as_percent_of_raw_cost}
{grid_lv_line_lifetime_in_years}


### Grid Low Voltage Connection
The low voltage connection connects a building to low voltage line.

* Initial Raw Cost is proportional to the estimated number of connections.
* Initial Installation Cost is proportional to the Raw Cost.
* Recurring Maintenance Cost is proportional to the Raw Cost.
* Recurring Replacement Cost is the Initial Cost divided by lifetime.

{grid_lv_connection_raw_cost}
{grid_lv_connection_installation_cost_as_percent_of_raw_cost}
{grid_lv_connection_maintenance_cost_per_year_as_percent_of_raw_cost}
{grid_lv_connection_lifetime_in_years}




## Technology: Diesel Mini Grid
A local diesel generator produces electricity that is distributed to consumers.

* Recurring Production Cost is the cost of fuel consumed. Multiply the fuel cost per liter, the fuel liters consumed per kilowatt-hour, the generator's capacity in kilowatts and its effective hours of production per year. The effective hours of production per year is the larger of either the loss-adjusted consumption per year divided by the system capacity or the minimum hours of production per year.

{diesel_mini_grid_system_loss_as_percent_of_total_production}
{diesel_mini_grid_fuel_cost_per_liter}


### Diesel Mini Grid Generator
Generators consume fuel to produce electricity.

* Initial Raw Cost
    * Size generator capacity based on estimated peak demand. Estimate the amount of loss-adjusted consumption that is happening during peak hours. Divide the loss-adjusted consumption by the number of peak hours per year to estimate peak demand.
    * Find the two generators that are closest to the desired capacity.
    * Compute the raw cost per unit capacity for each of the two selected generators.
    * Interpolate the raw cost per unit capacity relative to the desired capacity.
    * Multiply the raw cost per unit capacity by the desired capacity.
* Initial Installation Cost is proportional to the Raw Cost.
* Recurring Maintenance Cost is proportional to the Raw Cost.
* Recurring Replacement Cost is the Initial Cost divided by lifetime.

{diesel_mini_grid_generator_table: diesel mini grid generators}
{diesel_mini_grid_generator_minimum_hours_of_production_per_year}
{diesel_mini_grid_generator_fuel_liters_consumed_per_kwh}


### Diesel Mini Grid Low Voltage Line
The cost model is identical to grid low voltage line.

{diesel_mini_grid_lv_line_raw_cost_per_meter}
{diesel_mini_grid_lv_line_installation_cost_as_percent_of_raw_cost}
{diesel_mini_grid_lv_line_maintenance_cost_per_year_as_percent_of_raw_cost}
{diesel_mini_grid_lv_line_lifetime_in_years}


### Diesel Mini Grid Low Voltage Connection
The cost model is identical to grid low voltage connection.

{diesel_mini_grid_lv_connection_raw_cost}
{diesel_mini_grid_lv_connection_installation_cost_as_percent_of_raw_cost}
{diesel_mini_grid_lv_connection_maintenance_cost_per_year_as_percent_of_raw_cost}
{diesel_mini_grid_lv_connection_lifetime_in_years}




## Technology: Solar Home
A photovoltaic system produces electricity from sunlight for each [building](https://vimeo.com/158065353).

{solar_home_system_loss_as_percent_of_total_production}


### Solar Home Panel
The photovoltaic panel converts sunlight into electricity.

* Initial Raw Cost
    * Size panel capacity based on consumption. Since we have a battery, we do not need to consider peak demand and can use consumption directly.
    * Adjust consumption to account for system efficiency loss. Divide the loss adjusted consumption by the number of peak hours of sun per year to get desired panel capacity.
    * Find the two panels that are closest to the desired capacity.
    * Compute the raw cost per unit capacity for each of the two selected panels.
    * Interpolate the raw cost per unit capacity relative to the desired capacity.
    * Multiply the raw cost per unit capacity by the desired capacity.
* Initial Installation Cost is proportional to the Raw Cost.
* Recurring Maintenance Cost is proportional to the Raw Cost.
* Recurring Replacement Cost is the Initial Cost divided by lifetime.

{solar_home_panel_table: solar home panels}


### Solar Home Battery
Battery costs are proportional to panel costs.

{solar_home_battery_kwh_per_panel_kw}
{solar_home_battery_raw_cost_per_battery_kwh}
{solar_home_battery_installation_cost_as_percent_of_raw_cost}
{solar_home_battery_maintenance_cost_per_year_as_percent_of_raw_cost}
{solar_home_battery_lifetime_in_years}


### Solar Home Balance
Balance costs are proportional to panel costs.

{solar_home_balance_raw_cost_per_panel_kw}
{solar_home_balance_installation_cost_as_percent_of_raw_cost}
{solar_home_balance_maintenance_cost_per_year_as_percent_of_raw_cost}
{solar_home_balance_lifetime_in_years}




## Technology: Solar Mini Grid
A photovoltaic system produces electricity that is distributed to consumers.

{solar_mini_grid_system_loss_as_percent_of_total_production}


### Solar Mini Grid Panel
The photovoltaic panel converts sunlight into electricity.

* Initial Raw Cost
    * Size panel capacity based on consumption. Since we have a battery, we do not need to consider peak demand and can use consumption directly.
    * Adjust consumption to account for system efficiency loss. Divide the loss adjusted consumption by the number of peak hours of sun per year to get desired panel capacity.
    * Find the two panels that are closest to the desired capacity.
    * Compute the raw cost per unit capacity for each of the two selected panels.
    * Interpolate the raw cost per unit capacity relative to the desired capacity.
    * Multiply the raw cost per unit capacity by the desired capacity.
* Initial Installation Cost is proportional to the Raw Cost.
* Recurring Maintenance Cost is proportional to the Raw Cost.
* Recurring Replacement Cost is the Initial Cost divided by lifetime.

{solar_mini_grid_panel_table: solar mini grid panels}


### Solar Mini Grid Battery
Battery costs are proportional to panel costs.

{solar_mini_grid_battery_kwh_per_panel_kw}
{solar_mini_grid_battery_raw_cost_per_battery_kwh}
{solar_mini_grid_battery_installation_cost_as_percent_of_raw_cost}
{solar_mini_grid_battery_maintenance_cost_per_year_as_percent_of_raw_cost}
{solar_mini_grid_battery_lifetime_in_years}


### Solar Mini Grid Balance
Balance costs are proportional to panel costs.

{solar_mini_grid_balance_raw_cost_per_panel_kw}
{solar_mini_grid_balance_installation_cost_as_percent_of_raw_cost}
{solar_mini_grid_balance_maintenance_cost_per_year_as_percent_of_raw_cost}
{solar_mini_grid_balance_lifetime_in_years}


### Solar Mini Grid Low Voltage Line
The cost model is identical to grid low voltage line.

{solar_mini_grid_lv_line_raw_cost_per_meter}
{solar_mini_grid_lv_line_installation_cost_as_percent_of_raw_cost}
{solar_mini_grid_lv_line_maintenance_cost_per_year_as_percent_of_raw_cost}
{solar_mini_grid_lv_line_lifetime_in_years}


### Solar Mini Grid Low Voltage Connection
The cost model is identical to grid low voltage connection.

{solar_mini_grid_lv_connection_raw_cost}
{solar_mini_grid_lv_connection_installation_cost_as_percent_of_raw_cost}
{solar_mini_grid_lv_connection_maintenance_cost_per_year_as_percent_of_raw_cost}
{solar_mini_grid_lv_connection_lifetime_in_years}
