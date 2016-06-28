# Vision
Build a collection of tools for planning infrastructure.

# Mission
Implement solar mini grid cost model.

# Owner
Roy Hyunjin Han

# Context
The solar mini grid is a technology choice for local electricity generation and distribution that has recently become popular.

# Timeframe
20160627-1400 - 20160627-1700: 3 hours estimated

20160627-1400 - 20160627-1900: 5 hours actual

# Objectives
1. _ Draft solar mini grid cost model in a notebook.
2. _ Generate separate tool.
3. + Integrate module into integrated tool.

# Log
20160627-1530 - 20160627-1600: 30 minutes

	def estimate_internal_cost(**keywords):
        """
        Each function must return a dictionary with these keys:
            electricity_production_in_kwh_by_year
            electricity_production_cost_by_year
            electricity_internal_distribution_cost_by_year

        The keywords dictionary must contain these keys:
            financing_year
            discount_rate_as_percent_of_cash_flow_per_year
        """
		return prepare_internal_cost([
			estimate_electricity_production_cost,
			estimate_electricity_internal_distribution_cost,
		], keywords)

    from infrastructure_planning.electricity.cost import prepare_internal_cost

20160627-1600 - 20160627-1630: 30 minutes

    def estimate_electricity_production_cost(**keywords):
        return {
            'electricity_production_in_kwh_by_year': None,
            'electricity_production_cost_by_year': None,
            'electricity_internal_distribution_cost_by_year': None,
        }

    def estimate_electricity_internal_distribution_cost(**keywords):
        return {
            'electricity_production_in_kwh_by_year': None,
            'electricity_production_cost_by_year': None,
            'electricity_internal_distribution_cost_by_year': None,
        }

20160627-1630 - 20160627-1700: 30 minutes

    It actually turns out to be pretty simple.

    def estimate_electricity_production_cost(**keywords):
        d = prepare_component_cost_by_year([
            ('panel', estimate_panel_cost),
            ('battery', estimate_battery_cost),
            ('balance', estimate_balance_cost),
        ], keywords, prefix='solar_home_')
        solar_home_system_loss_as_percent_of_total_production = keywords[
            'solar_home_system_loss_as_percent_of_total_production']
        d['electricity_production_in_kwh_by_year'] = adjust_for_losses(
            keywords['consumption_in_kwh_by_year'],
            solar_home_system_loss_as_percent_of_total_production / 100.)
        d['electricity_production_cost_by_year'] = d.pop('cost_by_year')
        return d

    def estimate_electricity_internal_distribution_cost(
            **keywords):
        d = prepare_component_cost_by_year([
            ('lv_line', estimate_lv_line_cost),
            ('lv_connection', estimate_lv_connection_cost),
        ], keywords, prefix='solar_mini_grid_')
        d['electricity_internal_distribution_cost_by_year'] = d.pop('cost_by_year')
        return d

    _ Draft solar mini grid cost model in a notebook
    _ Generate separate tool
    + Integrate module into integrated tool
