"""
from infrastructure_planning.electricity.cost.solar_mini_grid import (
    estimate_internal_cost)


MAIN_FUNCTIONS = [
    estimate_internal_cost,
]


def run(g):
    g = prepare_parameters(g, NORMALIZED_NAME_BY_COLUMN_NAME)
    for f in MAIN_FUNCTIONS:
        graph = g['infrastructure_graph']
        for node_id, node_d in graph.nodes_iter(data=True):
            l = merge_dictionaries(node_d, {
                'node_id': node_id,
                'local_overrides': dict(g['demand_point_table'].ix[node_id])})
            try:
                node_d.update(compute(f, l, g))
            except InfrastructurePlanningError as e:
                exit('%s.error = %s : %s : %s' % (
                    e[0], l['name'].encode('utf-8'), f.func_name, e[1]))
    ls = [node_d for node_id, node_d in g[
        'infrastructure_graph'
    ].nodes_iter(data=True) if 'name' in node_d]  # Exclude fake nodes

    target_folder = g['target_folder']
    summary_folder = make_folder(join(target_folder, 'summary'))
    save_summary(summary_folder, ls, g, VARIABLE_NAMES)
    save_glossary(summary_folder, ls, g)
    return d


if __name__ == '__main__':
    argument_parser = ArgumentParser()
    argument_parser.add_argument(
        '-w', '--source_folder',
        metavar='FOLDER')
    argument_parser.add_argument(
        '-o', '--target_folder',
        metavar='FOLDER', type=make_folder)
    argument_parser.add_argument(
        '--json', action='store_true')

    argument_parser.add_argument(
        '--demand_point_table_path',
        metavar='PATH')

    args = argument_parser.parse_args()
    g = load_global_parameters(args.__dict__, __file__)
    g['demand_point_table'] = read_csv(g.pop('demand_point_table_path'))
    g['solar_mini_grid_panel_table'] = read_csv(g.pop(
        'solar_mini_grid_panel_table_path'))
    d = run(g)
    print(format_summary(d))
"""
