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
1. Fix bugs
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

# Tasks

    Get rid of underscores in columns
    Fix mv line assignments to node for mv lines to fake points
    Fix AttributeError: 'NoneType' object has no attribute 'is_aligned' for random geolocated cities
    Check duplicate keys in costs, examples, glossary

    Write test to make sure blank entries in local override columns use global value
    Write test to make sure local override for household consumption works
