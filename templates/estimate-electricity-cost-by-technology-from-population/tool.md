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
To override a computed value, upload a CSV with an additional column. The column name should match the name of the variable that you are overriding. Variable names are available in the CSV that is generated after running this tool.
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

#### Number of People per Connection
{number_of_people_per_connection}

#### Consumption in Kilowatt-Hours per Connection
{consumption_in_kwh_per_connection}

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

### Medium Voltage Line
Medium voltage lines carry electricity over large distances.

* Initial Installation Cost
    * Multiply the installation cost of MV line per meter by the number of meters of MV line in the network.
* Recurring Maintenance Cost
    * Multiply the maintenance cost of MV line per meter by the number of meters of MV line in the network.
* Recurring Replacement Cost
    * Divide the installation cost by the lifetime of MV line.

#### Grid Medium Voltage Network Minimum Point Count
{grid_mv_network_minimum_point_count}

#### Grid Medium Voltage Line (Existing)
{grid_mv_line_geotable}

#### Grid Medium Voltage Line Installation Labor and Material Cost per Meter
{grid_mv_line_installation_lm_cost_per_meter}

#### Grid Medium Voltage Line Maintenance Labor and Material Cost per Meter per Year
{grid_mv_line_maintenance_lm_cost_per_meter_per_year}

#### Grid Medium Voltage Line Lifetime in Years
{grid_mv_line_lifetime_in_years}

### Medium Voltage Transformer
Medium voltage transformers convert medium voltage to low voltage.

* Initial Installation Cost
    * The cost of a transformer depends on its capacity, which is how much electricity it can deliver. Transformer capacity is listed in kVA. If the power factor of the load is 0.85, then the number of kWh delivered is kVA * 0.85.
    * Size transformer capacity based on estimated peak demand. Estimate the amount of loss-adjusted consumption that is happening during peak hours. Divide the loss-adjusted consumption by the number of peak hours per year to estimate peak demand.
    * Select the largest transformer capacity that will satisfy the estimated peak demand.
    * Estimate the number of those transformers that will satisfy the estimated peak demand.
    * Estimate the installation cost by multiplying the installation cost of the selected transformer by the number of transformers.
* Recurring Maintenance Cost
    * Multiply the maintenance cost per year of the selected transformer by the number of transformers.
* Recurring Replacement Cost
    * Divide the installation cost by the lifetime of the selected transformer.

#### Grid Medium Voltage Transformer Load Power Factor
{grid_mv_transformer_load_power_factor}

#### Grid Medium Voltage Transformer Table
{grid_mv_transformer_table}

### Low Voltage Line
Low voltage lines distribute electricity over small distances.

* Initial Installation Cost
    * Multiply the installation cost of LV line per meter by the estimated number of meters of LV line.
    * The number of meters of LV line is the number of connections multiplied by the average distance between buildings.
* Recurring Maintenance Cost
    * Multiply the maintenance cost of LV line per meter by the number of meters of LV line.
* Recurring Replacement Cost
    * Divide the installation cost by the lifetime of LV line.

#### Grid Low Voltage Line Installation Labor and Material Cost per Meter
{grid_lv_line_installation_lm_cost_per_meter}

#### Grid Low Voltage Line Maintenance Labor and Material Cost per Meter per Year
{grid_lv_line_maintenance_lm_cost_per_meter_per_year}

#### Grid Low Voltage Line Lifetime in Years
{grid_lv_line_lifetime_in_years}

### Low Voltage Connection
The low voltage connection connects a building to low voltage line.

* Initial Installation Cost
    * Multiply the installation cost per connection by the estimated number of connections.
* Recurring Maintenance Cost
    * Multiply the maintenance cost per connection by the estimated number of connections.
* Recurring Replacement Cost
    * Divide the installation cost by the lifetime of the connection to estimate the replacement cost per year.

#### Grid Low Voltage Connection Installation Labor and Material Cost per Connection
{grid_lv_connection_installation_lm_cost_per_connection}

#### Grid Low Voltage Connection Maintenance Labor and Material Cost per Connection per Year
{grid_lv_connection_maintenance_lm_cost_per_connection_per_year}

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

* Initial Installation Cost
    * Size generator capacity based on estimated peak demand. Estimate the amount of loss-adjusted consumption that is happening during peak hours. Divide the loss-adjusted consumption by the number of peak hours per year to estimate peak demand.
    * Select the largest generator capacity that will satisfy the estimated peak demand.
    * Estimate the number of those generators that will satisfy the estimated peak demand.
    * Estimate the installation cost by multiplying the installation cost of the selected generator by the number of generators.
* Recurring Maintenance Cost
    * Multiply the maintenance cost per year of the selected generator by the number of generators.
* Recurring Replacement Cost
    * Divide the installation cost by the lifetime of the selected generator.

#### Diesel Mini Grid Generator
{diesel_mini_grid_generator_table}

#### Diesel Mini Grid Generator Minimum Hours of Production per Year
{diesel_mini_grid_generator_minimum_hours_of_production_per_year}

#### Diesel Mini Grid Generator Fuel Liters Consumed per Kilowatt-Hour
{diesel_mini_grid_generator_fuel_liters_consumed_per_kwh}

### Low Voltage Line
The cost model is identical to grid low voltage line.

#### Diesel Mini Grid Low Voltage Line Installation Labor and Material Cost per Meter
{diesel_mini_grid_lv_line_installation_lm_cost_per_meter}

#### Diesel Mini Grid Low Voltage Line Maintenance Labor and Material Cost per Meter per Year
{diesel_mini_grid_lv_line_maintenance_lm_cost_per_meter_per_year}

#### Diesel Mini Grid Low Voltage Line Lifetime in Years
{diesel_mini_grid_lv_line_lifetime_in_years}

### Low Voltage Connection

#### Diesel Mini Grid Low Voltage Connection Installation Labor and Material Cost per Connection
{diesel_mini_grid_lv_connection_installation_lm_cost_per_connection}

#### Diesel Mini Grid Low Voltage Connection Maintenance Labor and Material Cost per Connection per Year
{diesel_mini_grid_lv_connection_maintenance_lm_cost_per_connection_per_year}

#### Diesel Mini Grid Low Voltage Connection Lifetime in Years
{diesel_mini_grid_lv_connection_lifetime_in_years}


## Technology: Solar Home System
A photovoltaic system produces electricity from sunlight for each [building](https://vimeo.com/158065353).

#### Solar Home System Loss as Percent of Total Production
{solar_home_system_loss_as_percent_of_total_production}

### Panel
The photovoltaic panel converts sunlight into electricity.

* Initial Installation Cost
    * Size panel capacity based on consumption. Since we have a battery, we do not need to consider peak demand and can use consumption directly.
    * Adjust consumption to account for system efficiency loss. Divide the loss adjusted consumption by the number of peak hours of sun per year to get desired panel capacity.
    * Select the largest panel capacity that will satisfy the desired panel capacity.
    * Estimate the number of those panels that will satisfy the desired panel capacity.
* Recurring Maintenance Cost
    * Multiply the maintenance cost per year of the selected panel by the number of panels.
* Recurring Replacement Cost
    * Divide the installation cost by the lifetime of the selected panel.

#### Solar Home System Panel Table
{solar_home_panel_table}

### Battery
Battery costs are proportional to panel costs.

#### Solar Home System Battery Storage Size in Kilowatt-Hours per Panel Kilowatt
{solar_home_battery_kwh_per_panel_kw}

#### Solar Home System Battery Installation Labor and Material Cost per Battery Kilowatt-Hour
{solar_home_battery_installation_lm_cost_per_battery_kwh}

#### Solar Home System Battery Maintenance Labor and Material Cost per Kilowatt-Hour per Year
{solar_home_battery_maintenance_lm_cost_per_kwh_per_year}

#### Solar Home System Battery Lifetime in Years
{solar_home_battery_lifetime_in_years}

### Balance
Balance costs are proportional to panel costs.

#### Solar Home System Balance Installation Labor and Material Cost per Panel Kilowatt
{solar_home_balance_installation_lm_cost_per_panel_kw}

#### Solar Home System Balance Maintenance Labor and Material Cost per Panel Kilowatt per Year
{solar_home_balance_maintenance_lm_cost_per_panel_kw_per_year}

#### Solar Home System Balance Lifetime in Years
{solar_home_balance_lifetime_in_years}
