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

20160613-1100 - 20160830-1545: 3 months actual

# Objectives
1. _ Derive default values for Leona in Senegal.
2. _ Derive default values for Kaduna in Nigeria.
3. _ Draft some notes on how to derive certain values.

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

20160830-1530 - 20160830-1545: 15 minutes

    _ Write script to convert old parameters to new parameters
    _ Draft JSON file from Senegal defaults
    _ Draft JSON file from Nigeria defaults
    _ Revise parameter defaults to fit Nigeria defaults

Although a conversion script might have some use, its lifespan will be limited as people move to the new system. We'll let the users create default values for different countries.
