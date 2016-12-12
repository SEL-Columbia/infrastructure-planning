# Vision

Build second-generation infrastructure planning system.

# Mission

Prepare system for second production release.

# Owner

Roy Hyunjin Han

# Context

It is important to keep the project alive while it still has users.

# Timeframe

20161212-1000 - 20161222-1000: 10 days estimated

# Objectives

1. Sort goals.
2. Fix bugs.
3. Update model.

# Log

20161212-1015 - 20161212-1045: 30 minutes

    _ Rename standard_output.log to stdout.log
    _ Rename standard_error.log to stderr.log
    _ Get default parameters for tanzania training
    + Check that everything still works

20161212-1100 - 20161212-1200: 1 hour

I found a serious bug in the way that values are being interpolated in `interpolate_values`.

    Use parameters from minimum capacity if actual is less than minimum

# Tasks

    Consider total population and % connected to compute unconnected household count
        Grow population using total population
        Size capacity using unconnected household count
    Consider estimating population growth using projected population year
    Let user download example table for each table
    Update executive summary by technology
        Show connection count
