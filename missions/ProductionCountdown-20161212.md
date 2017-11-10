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

    + Use parameters from minimum capacity if actual is less than minimum

20170224-1715 - 20170224-1800: 45 minutes

    _ Consider renaming selected_technologies to ordered_technologies or ranked_technologies
    + Rename selected_technologies_text to technology_options

20170227-1600 - 20170227-1730: 90 minutes

    + Update template to display properly
    + Add github link to template

# Tasks

    Make sure technology_options work properly
    Add help text based on Shaky's data dictionary

    Rename "proposed cost per connection" to "proposed discounted cost per connection"
    Add "proposed initial cost per connection" to report by location

    Consider total population and % connected to compute unconnected household count
        Rename household count to unconnected household count
        Rename population count to unconnected population count
        Grow population using total population
        Size capacity using unconnected household count
        Add preconnected_technology
            Use grid if preconnected_technology or proposed_technology is grid
            Use proposed technology if both are not grid
            Include capital costs if there is a change
            Exclude capital costs if there is no change
            Include recurring costs in both cases
        Add preconnected_rate_as_percent_of_population
            Compute unelectrified population
            Grow the full population
            Use unelectrified population for calculations
    Consider estimating population growth using projected population year

    Update executive summary by technology
        Show connection count

    Consider simplifying existing mv lines with line simplification
    Speed up networker with line simplification

    Rename tool to something shorter like Electrification Planning
    Move parameter and argument descriptions into mouseover popups

    Have population growth stop at a specific year
    Show connection count in executive summary
    Make it possible to specify single values as an alternative to tables
    Implement % connected for electricity intensification
    Rewrite sequencer

    Draw break even analysis graph with revenue, variable costs, fixed costs, gross profit
    Highlight towns that could result in sustainable utility companies

    Consider altitude
    Include roads
