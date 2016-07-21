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

    Check duplicate keys in costs, examples, glossary

# Tasks

    Consider total population and % connected to compute (unconnected) household count as suggested by Edwin

    Write test to make sure blank entries in local override columns use global value
    Write test to make sure local override for household consumption works

    Update output files
        Include essential properties in shapefile
            https://github.com/SEL-Columbia/infrastructure-planning/issues/3
            Check shapefile column name length limit
        Clean up output folder
            /result.cfg
            /run.sh
            /stdout.log
            /stderr.log
            /infrastructure_map.csv
            /infrastructure_summary.csv
            /infrastructure_details.csv
            /infrastructure_graph.json
            /summary/parameters.json
            /summary/points.csv
            /summary/points.shp
            /summary/lines.csv
            /summary/lines-existing.shp
            /summary/lines-proposed.shp
            /summary/costs.csv
        Rename to existing mv line and proposed mv line

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

    Check pull request for networker
    Submit pull request for sequencer
        git diff 2115bb0aeecf5e6e0b15d2a37513294aa0874f8e | grep diff
        diff --git a/.gitignore b/.gitignore
        diff --git a/demo_sequencer.py b/demo_sequencer.py
        diff --git a/requirements.txt b/requirements.txt
        diff --git a/sequencer/Models.py b/sequencer/Models.py
        diff --git a/sequencer/NetworkPlan.py b/sequencer/NetworkPlan.py
        diff --git a/sequencer/Sequencer.py b/sequencer/Sequencer.py
        diff --git a/sequencer/Utils.py b/sequencer/Utils.py

    Prepare for production
        Write positive test

    Separate calculator and aggregator
        Have calculator generate geojson file

    Update interface
        Show overrided columns
        Let user download example table for each table
        Add acknowledgments to integrated tool

        Look into issues with live table override
        Show simple map in addition to satellite map
        Make existing grid a different color or stroke
        Consider letting user add row or column

    Update validation
        https://github.com/SEL-Columbia/infrastructure-planning/issues/5
        Consider how to send error messages regarding invalid numbers with commas

    Add instructions on how to set up the system on a new machine
