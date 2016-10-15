from networker.networker_runner import NetworkerRunner
from os.path import join
from sequencer import NetworkPlan, Sequencer

from ..macros import get_table_from_graph, save_shapefile


def assemble_total_grid_mv_line_network(
        target_folder, infrastructure_graph, grid_mv_line_geotable,
        grid_mv_network_minimum_point_count):
    graph = infrastructure_graph
    node_table = get_table_from_graph(graph, [
        'longitude', 'latitude', 'grid_mv_line_adjusted_budget_in_meters'])
    node_table_path = join(target_folder, 'nodes-networker.csv')
    node_table.to_csv(node_table_path)
    nwk_settings = {
        'demand_nodes': {
            'filename': node_table_path,
            'x_column': 'longitude',
            'y_column': 'latitude',
            'budget_column': 'grid_mv_line_adjusted_budget_in_meters',
        },
        'network_algorithm': 'mod_boruvka',
        'network_parameters': {
            'minimum_node_count': grid_mv_network_minimum_point_count,
        },
    }
    if len(grid_mv_line_geotable):
        grid_mv_line_shapefile_path = join(
            target_folder, 'existing_grid_mv_line.shp')
        save_shapefile(grid_mv_line_shapefile_path, grid_mv_line_geotable)
        nwk_settings['existing_networks'] = {
            'filename': grid_mv_line_shapefile_path,
            'budget_value': 0,
        }
    nwk = NetworkerRunner(nwk_settings, target_folder)
    nwk.validate()
    msf = nwk.run()
    for node_id in msf.nodes_iter():
        if node_id in graph:
            continue
        # Add fake nodes (I think that is what these are)
        longitude, latitude = msf.coords[node_id]
        graph.add_node(node_id, {
            'longitude': longitude,
            'latitude': latitude,
            'population': 0,
            'peak_demand_in_kw': 0,
        })
    graph.add_edges_from(msf.edges_iter())
    return {'infrastructure_graph': graph}


def sequence_total_grid_mv_line_network(target_folder, infrastructure_graph):
    graph = infrastructure_graph
    if not graph.edges():
        return {}  # The network is empty and there is nothing to sequence
    node_table = get_table_from_graph(graph, [
        'longitude', 'latitude', 'population', 'peak_demand_in_kw'])
    node_table = node_table.rename(columns={'longitude': 'X', 'latitude': 'Y'})
    node_table_path = join(target_folder, 'nodes-sequencer.csv')
    node_table.to_csv(node_table_path)
    edge_shapefile_path = join(target_folder, 'edges.shp')
    nwp = NetworkPlan.from_files(
        edge_shapefile_path, node_table_path, prioritize='population',
        proj='+proj=longlat +datum=WGS84 +no_defs')
    model = Sequencer(nwp, 'peak.demand.in.kw')
    model.sequence()
    order_series = model.output_frame['Sequence..Far.sighted.sequence']
    for index, order in order_series.iteritems():
        node_id = model.output_frame['Unnamed..0'][index]
        graph.node[node_id]['order'] = order
    return {'infrastructure_graph': graph}
