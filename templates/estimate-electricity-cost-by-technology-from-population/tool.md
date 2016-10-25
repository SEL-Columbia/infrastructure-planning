# Estimate Electricity Cost by Technology from Population
Each technology has initial installation costs and recurring production, maintenance and replacement costs.

Mini-grid technologies include a central production facility and a low-voltage distribution network.

#### Selected Technologies
{selected_technologies_text}


## Finance
The amount of money needed to fund an infrastructure project includes both initial and recurring costs. The initial costs are paid upfront and the recurring costs are paid later.

The net present value or discounted cost of an infrastructure project assumes that you will invest the money that you are not using now. For example, if a $110k project will start next year and if you are confident that you will earn at least 10% through investments, then you can request a loan for $100k one year in advance.

#### Year of Financing
{financing_year}

#### Time Horizon in Years
{time_horizon_in_years}

#### Discount Rate as Percent of Cash Flow per Year
{discount_rate_as_percent_of_cash_flow_per_year}


## Demography
Assume that population grows at a fixed rate each year. If the population is 100 and the growth rate is 10%, then the population will be 110 after the first year and 121 after the second year.

#### Demand Point Table
To override a computed value for specific demand points, upload a CSV with an additional column. The column name should match the name of the variable that you are overriding. Variable names are available in the *glossary.csv* file that is generated after running this tool.

Note that if you leave a blank entry in a local override column, then the system will not override the value for that demand point.

{demand_point_table}

#### Population Year
{population_year}

#### Population Growth Rate as Percent of Population per Year
{population_growth_as_percent_of_population_per_year}


## Geography

#### Line Length Adjustment Factor
The length of line used to connect two locations is often greater than the distance between the two locations.

{line_length_adjustment_factor}

#### Average Distance Between Buildings in Meters
{average_distance_between_buildings_in_meters}

#### Peak Hours of Sun per Year
{peak_hours_of_sun_per_year}


## Consumption
Assume that consumption is fixed per capita. Estimate consumption based on the projected population.

#### Connection Type Table
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

{connection_type_table}

#### Number of People per Household
{number_of_people_per_household}

#### Consumption during Peak Hours as Percent of Total Consumption
{consumption_during_peak_hours_as_percent_of_total_consumption}

#### Peak Hours of Consumption per Year
{peak_hours_of_consumption_per_year}


## Technology: Grid
A remote source produces electricity that is distributed to consumers.

* Recurring Production Cost
    * Assume that we must produce more than what we consume because of distribution losses.
    * Production cost is the loss-adjusted local consumption in kWh multiplied by the electricity production cost per kWh.

#### Grid Electricity Production Cost per Kilowatt-Hour
{grid_electricity_production_cost_per_kwh}

#### Grid System Loss as Percent of Total Production
{grid_system_loss_as_percent_of_total_production}

### Grid Medium Voltage Line
Medium voltage lines carry electricity over large distances.

* Initial Raw Cost is proportional to the number of meters of medium voltage line in the network.
* Initial Installation Cost is proportional to the Raw Cost.
* Recurring Maintenance Cost is proportional to the Raw Cost.
* Recurring Replacement Cost is the Initial Cost divided by lifetime.

#### Grid Medium Voltage Network Minimum Point Count
{grid_mv_network_minimum_point_count}

#### Grid Medium Voltage Line (Existing)
{grid_mv_line_geotable}

#### Grid Medium Voltage Line Raw Cost per Meter
{grid_mv_line_raw_cost_per_meter}

#### Grid Medium Voltage Line Installation Cost as Percent of Raw Cost
{grid_mv_line_installation_cost_as_percent_of_raw_cost}

#### Grid Medium Voltage Line Maintenance Cost per Year as Percent of Raw Cost
{grid_mv_line_maintenance_cost_per_year_as_percent_of_raw_cost}

#### Grid Medium Voltage Line Lifetime in Years
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

#### Grid Medium Voltage Transformer Load Power Factor
{grid_mv_transformer_load_power_factor}

#### Grid Medium Voltage Transformer Table
{grid_mv_transformer_table}

### Grid Low Voltage Line
Low voltage lines distribute electricity over small distances.

* Initial Raw Cost
    * Multiply the raw cost of low voltage line per meter by the estimated number of meters of low voltage line.
    * The number of meters of LV line is the number of connections multiplied by the average distance between buildings.
* Initial Installation Cost is proportional to the Raw Cost.
* Recurring Maintenance Cost is proportional to the Raw Cost.
* Recurring Replacement Cost is the Initial Cost divided by lifetime.

#### Grid Low Voltage Line Raw Cost per Meter
{grid_lv_line_raw_cost_per_meter}

#### Grid Low Voltage Line Installation Cost as Percent of Raw Cost
{grid_lv_line_installation_cost_as_percent_of_raw_cost}

#### Grid Low Voltage Line Maintenance Cost per Year as Percent of Raw Cost
{grid_lv_line_maintenance_cost_per_year_as_percent_of_raw_cost}

#### Grid Low Voltage Line Lifetime in Years
{grid_lv_line_lifetime_in_years}

### Grid Low Voltage Connection
The low voltage connection connects a building to low voltage line.

* Initial Raw Cost is proportional to the estimated number of connections.
* Initial Installation Cost is proportional to the Raw Cost.
* Recurring Maintenance Cost is proportional to the Raw Cost.
* Recurring Replacement Cost is the Initial Cost divided by lifetime.

#### Grid Low Voltage Connection Raw Cost
{grid_lv_connection_raw_cost}

#### Grid Low Voltage Connection Installation Cost as Percent of Raw Cost
{grid_lv_connection_installation_cost_as_percent_of_raw_cost}

#### Grid Low Voltage Connection Maintenance Cost per Year as Percent of Raw Cost
{grid_lv_connection_maintenance_cost_per_year_as_percent_of_raw_cost}

#### Grid Low Voltage Connection Lifetime in Years
{grid_lv_connection_lifetime_in_years}


## Technology: Diesel Mini Grid
A local diesel generator produces electricity that is distributed to consumers.

* Recurring Production Cost
    * The cost of fuel consumed is the product of the fuel cost per liter, the fuel liters consumed per kilowatt-hour, the generator's capacity in kilowatts and its effective hours of production per year. The effective hours of production per year is the larger of either the loss-adjusted consumption per year divided by the system capacity or the minimum hours of production per year.

#### Diesel Mini Grid System Loss as Percent of Total Production
{diesel_mini_grid_system_loss_as_percent_of_total_production}

#### Diesel Mini Grid Fuel Cost per Liter
{diesel_mini_grid_fuel_cost_per_liter}

### Generator
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

#### Diesel Mini Grid Generator
{diesel_mini_grid_generator_table}

#### Diesel Mini Grid Generator Minimum Hours of Production per Year
{diesel_mini_grid_generator_minimum_hours_of_production_per_year}

#### Diesel Mini Grid Generator Fuel Liters Consumed per Kilowatt-Hour
{diesel_mini_grid_generator_fuel_liters_consumed_per_kwh}

### Diesel Mini Grid Low Voltage Line
The cost model is identical to grid low voltage line.

#### Diesel Mini Grid Low Voltage Line Raw Cost per Meter
{diesel_mini_grid_lv_line_raw_cost_per_meter}

#### Diesel Mini Grid Low Voltage Line Installation Cost as Percent of Raw Cost
{diesel_mini_grid_lv_line_installation_cost_as_percent_of_raw_cost}

#### Diesel Mini Grid Low Voltage Line Maintenance Cost per Year as Percent of Raw Cost
{diesel_mini_grid_lv_line_maintenance_cost_per_year_as_percent_of_raw_cost}

#### Diesel Mini Grid Low Voltage Line Lifetime in Years
{diesel_mini_grid_lv_line_lifetime_in_years}

### Diesel Mini Grid Low Voltage Connection

#### Diesel Mini Grid Low Voltage Connection Raw Cost
{diesel_mini_grid_lv_connection_raw_cost}

#### Diesel Mini Grid Low Voltage Connection Installation Cost as Percent of Raw Cost
{diesel_mini_grid_lv_connection_installation_cost_as_percent_of_raw_cost}

#### Diesel Mini Grid Low Voltage Connection Maintenance Cost per Year as Percent of Raw Cost
{diesel_mini_grid_lv_connection_maintenance_cost_per_year_as_percent_of_raw_cost}

#### Diesel Mini Grid Low Voltage Connection Lifetime in Years
{diesel_mini_grid_lv_connection_lifetime_in_years}


## Technology: Solar Home System
A photovoltaic system produces electricity from sunlight for each [building](https://vimeo.com/158065353).

#### Solar Home System Loss as Percent of Total Production
{solar_home_system_loss_as_percent_of_total_production}

### Panel
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

#### Solar Home System Panel Table
{solar_home_panel_table}

### Battery
Battery costs are proportional to panel costs.

#### Solar Home System Battery Storage Size in Kilowatt-Hours per Panel Kilowatt
{solar_home_battery_kwh_per_panel_kw}

#### Solar Home System Battery Raw Cost per Battery Kilowatt-Hour
{solar_home_battery_raw_cost_per_battery_kwh}

#### Solar Home System Battery Installation Cost as Percent of Raw Cost
{solar_home_battery_installation_cost_as_percent_of_raw_cost}

#### Solar Home System Battery Maintenance Cost per Year as Percent of Raw Cost
{solar_home_battery_maintenance_cost_per_year_as_percent_of_raw_cost}

#### Solar Home System Battery Lifetime in Years
{solar_home_battery_lifetime_in_years}

### Balance
Balance costs are proportional to panel costs.

#### Solar Home System Balance Raw Cost per Panel Kilowatt
{solar_home_balance_raw_cost_per_panel_kw}

#### Solar Home System Balance Installation Cost as Percent of Raw Cost
{solar_home_balance_installation_cost_as_percent_of_raw_cost}

#### Solar Home System Balance Maintenance Cost per Year as Percent of Raw Cost
{solar_home_balance_maintenance_cost_per_year_as_percent_of_raw_cost}

#### Solar Home System Balance Lifetime in Years
{solar_home_balance_lifetime_in_years}


## Technology: Solar Mini Grid
A photovoltaic system produces electricity that is distributed to consumers.

#### Solar Mini Grid System Loss as Percent of Total Production
{solar_mini_grid_system_loss_as_percent_of_total_production}

### Panel
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

#### Solar Mini Grid System Panel Table
{solar_mini_grid_panel_table}

### Battery
Battery costs are proportional to panel costs.

#### Solar Mini Grid System Battery Storage Size in Kilowatt-Hours per Panel Kilowatt
{solar_mini_grid_battery_kwh_per_panel_kw}

#### Solar Mini Grid System Battery Raw Cost per Battery Kilowatt-Hour
{solar_mini_grid_battery_raw_cost_per_battery_kwh}

#### Solar Mini Grid System Battery Installation Cost as Percent of Raw Cost
{solar_mini_grid_battery_installation_cost_as_percent_of_raw_cost}

#### Solar Mini Grid System Battery Maintenance Cost per Year as Percent of Raw Cost
{solar_mini_grid_battery_maintenance_cost_per_year_as_percent_of_raw_cost}

#### Solar Mini Grid System Battery Lifetime in Years
{solar_mini_grid_battery_lifetime_in_years}

### Balance
Balance costs are proportional to panel costs.

#### Solar Mini Grid System Balance Raw Cost per Panel Kilowatt
{solar_mini_grid_balance_raw_cost_per_panel_kw}

#### Solar Mini Grid System Balance Installation Cost as Percent of Raw Cost
{solar_mini_grid_balance_installation_cost_as_percent_of_raw_cost}

#### Solar Mini Grid System Balance Maintenance Cost per Year as Percent of Raw Cost
{solar_mini_grid_balance_maintenance_cost_per_year_as_percent_of_raw_cost}

#### Solar Mini Grid System Balance Lifetime in Years
{solar_mini_grid_balance_lifetime_in_years}

### Solar Mini Grid Low Voltage Line
The cost model is identical to grid low voltage line.

#### Solar Mini Grid Low Voltage Line Raw Cost per Meter
{solar_mini_grid_lv_line_raw_cost_per_meter}

#### Solar Mini Grid Low Voltage Line Installation Cost as Percent of Raw Cost
{solar_mini_grid_lv_line_installation_cost_as_percent_of_raw_cost}

#### Solar Mini Grid Low Voltage Line Maintenance Cost per Year as Percent of Raw Cost
{solar_mini_grid_lv_line_maintenance_cost_per_year_as_percent_of_raw_cost}

#### Solar Mini Grid Low Voltage Line Lifetime in Years
{solar_mini_grid_lv_line_lifetime_in_years}

### Solar Mini Grid Low Voltage Connection

#### Solar Mini Grid Low Voltage Connection Raw Cost
{solar_mini_grid_lv_connection_raw_cost}

#### Solar Mini Grid Low Voltage Connection Installation Cost as Percent of Raw Cost
{solar_mini_grid_lv_connection_installation_cost_as_percent_of_raw_cost}

#### Solar Mini Grid Low Voltage Connection Maintenance Cost per Year as Percent of Raw Cost
{solar_mini_grid_lv_connection_maintenance_cost_per_year_as_percent_of_raw_cost}

#### Solar Mini Grid Low Voltage Connection Lifetime in Years
{solar_mini_grid_lv_connection_lifetime_in_years}
