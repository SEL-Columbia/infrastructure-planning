# Tasks

    Consider including altitude for each point
    Consider supporting multiple transformer table override
    Let user override transformer cost per kva

    Let user download example table for each table
    Prepare Spanish Language template
    Consider supporting capacity and installation cost per kw override
    Use same colours for technologies
    Add legend for technologies
    Consider preserving datetime fields in shapefiles

## Important and easy

    Update executive summary by technology
        Show initial cost
        Show projected recurring
        Show levelized cost
        Show location count
        Show population count
        Show initial cost per connection
        Show capacity per household
    Add household count and total and existing proposed grid length to summary

    Adjust map colors to match old system
    Add legend to map
    Allow striped stroke for map lines

    Check for required columns like name
    Replace geopy geocoding with error message about expected longitude latitude
    Check that name supports unicode

    Sort add_argument statements by function
    Split save_total_map

    Add technology cost multiplier
    Update estimate_diesel_mini_grid_fuel_cost to vary based on generator capacity

    Add warning if peak_demand_in_kw is nan or zero
    Use global value if local value is nan
    Test that we only use most recent year if multiple years are given
    Handle empty null values for number of people per household

    Replace peak_demand with household and population info when clicking on node

    Test for unelectrified option
    Test that command line argument can override json
    Test when there are demand points but no consumption
    Test when there are no demand points
    Write positive test

    Explain that network minimum point is minimum size of grid network
    Explain that electricity cost per kwh is the same as busbar cost
    Explain that technologies chosen via networker not in coster #10

    Write estimate_grid_mv_line_budget_in_meters to duplicate the beginning part of the script
    Check if we can override selected_technologies on a local basis

    Add instructions on how to set up the system on a new machine
        Update installation requirements
    Draft jupyter notebook that starts from the population of a single node

## Important and hard

    Have single rows replace tables
    Convert tools into jupyter notebooks
        Make notebook for each technology that models only that technology

## Unimportant and easy

    Write test to make sure blank entries in local override columns use global value
    Write test to make sure local override for household consumption works
    Make sure that capacities in tables are greater than zero
    Make sure that lifetimes in tables are greater than zero

    Note that diesel mini grid is night time
    Note that solar home system might have all sun in summer and none in winter
    Consider splitting line_length_adjustment_factor for lv and mv
    Consider separating distribution loss and system loss

    Get bullet points of possible components of system loss for documentation
    Document ways that users can debug model

    Show overrided columns
    Show simple map in addition to satellite map

    Add meta tool to explore demand threshold by varying household demand to change mvMax
    Consider tools that fill certain values based on administrative boundary
    Consider tools that fill certain values based on urban vs rural

    Cite "Total population, both sexes combined (thousands)" http://data.un.org/Data.aspx?d=PopDiv&f=variableID%3A12
    Cite "City population by sex, city and city type" http://data.un.org/Data.aspx?d=POP&f=tableCode:240
    Cite "Electric power consumption (kWh per capita)" http://data.worldbank.org/indicator/EG.USE.ELEC.KH.PC
    Cite "CIA World Factbook" https://www.cia.gov/library/publications/the-world-factbook/fields/2002.html
    Cite "GDP growth (annual %)" http://data.worldbank.org/indicator/NY.GDP.MKTP.KD.ZG
    Cite "Electric Sales, Revenue, and Average Price"
        http://www.eia.gov/electricity/sales_revenue_cost/index.cfm
        http://www.eia.gov/electricity/sales_revenue_cost/xls/table10.xls
    Update compute-discounted-cost
        Define loan_year in compute discounted cost
        Check whether different loan year affects breakeven time (whether we need to add loan year)

    Check that time_horizon_in_years is positive
    Make grid.estimate_electricity_production_cost consistent

## Unimportant and hard

    Look at label for node and compute metrics by cluster
    Look into issues adjusting table values directly on page
    Show proposed network in different color or style from existing
    Move grow_exponentially into growth
    Make similar functions consistent with each other
    Consider letting user add row or column
    Consider accepting net present value vs consumption curve for energy source X
    Consider estimate line length more accurately using elevation if available via linestring z
    Gather past datasets and write tests to make sure the models run successfully on each of them
