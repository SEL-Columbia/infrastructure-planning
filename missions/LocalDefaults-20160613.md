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

I might need a step by step document that shows how to convert paramets from the old NetworkPlanner to the new infrastructure-planning system.

# Tasks

    Check which Senegal defaults correspond to old defaults from network-planner
    Draft JSON file from Senegal defaults in configuration file
    Draft JSON file from Nigeria defaults
    Revise parameter defaults to fit Nigeria defaults

    Draft step by step tutorial for converting from old NetworkPlanner parameters to new infrastructure-planning parameters
