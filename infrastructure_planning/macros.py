import inspect
import simplejson as json
import shutil
from collections import OrderedDict
from invisibleroads_macros.disk import make_enumerated_folder_for, make_folder
from invisibleroads_macros.iterable import merge_dictionaries
from invisibleroads_macros.math import divide_safely
from invisibleroads_macros.table import normalize_column_name
from networkx import Graph, write_gpickle
from os.path import isabs, join, splitext
from pandas import DataFrame, Series, concat, isnull
from shapely.geometry import LineString, Point

from .exceptions import (
    ExpectedPositive, InfrastructurePlanningError, ValidationError)
from .parsers import load_files


def load_and_run(normalization_functions, main_functions, argument_parser):
    args = argument_parser.parse_args()
    g = load_arguments(args.__dict__)
    save_arguments(g, __file__)
    try:
        g = load_files(g)
        g = normalize_arguments(normalization_functions, g)
        d = run(main_functions, g)
    except InfrastructurePlanningError as e:
        exit(e)
    for k, v in d.items():
        print('%s = %s' % (k, v))
    return d


def load_arguments(value_by_key):
    configuration_path = value_by_key.pop('configuration_path')
    source_folder = value_by_key.pop('source_folder')
    g = json.load(open(configuration_path)) if configuration_path else {}
    # Command-line arguments override configuration arguments
    for k, v in value_by_key.items():
        if v is None:
            continue
        g[k] = v
    # Resolve relative paths using source_folder
    if source_folder:
        for k, v in g.items():
            if k.endswith('_path') and v and not isabs(v):
                g[k] = join(source_folder, v)
    return g


def save_arguments(g, script_path):
    d = g.copy()
    target_folder = d.pop('target_folder')
    if not target_folder:
        target_folder = make_enumerated_folder_for(script_path)
    arguments_folder = make_folder(join(target_folder, 'arguments'))
    for k, v in d.items():
        if not k.endswith('_path'):
            continue
        file_name = _get_argument_file_name(k, v)
        # Save a copy of each file
        shutil.copy(v, join(arguments_folder, file_name))
        # Make the reference point to the local copy
        d[k] = file_name
    # Save global arguments
    json.dump(d, open(join(arguments_folder, 'arguments.json'), 'w'))
    g['target_folder'] = target_folder


def normalize_arguments(normalization_functions, g):
    errors = []
    # Normalize columns
    for k, v in g.items():
        if not hasattr(v, 'columns'):
            continue
        v.columns = [normalize_column_name(x, '_') for x in v.columns]
    # Normalize tables
    for normalize_argument in normalization_functions:
        try:
            g.update(compute(normalize_argument, g))
        except ValidationError as e:
            print(e)
            errors.append(e)
    # Make decision
    if errors:
        raise InfrastructurePlanningError('could not normalize arguments')
    return g


def run(main_functions, g):
    g['infrastructure_graph'] = get_graph_from_table(g['demand_point_table'])

    for f in main_functions:
        if '_total_' in f.func_name:
            g.update(compute(f, g))
            continue
        for node_id, node_d in g['infrastructure_graph'].nodes_iter(data=True):
            if 'name' not in node_d:
                continue  # We have a fake node
            l = merge_dictionaries(node_d, {
                'node_id': node_id,
                'local_overrides': dict(g['demand_point_table'].ix[node_id])})
            node_d.update(compute(f, l, g))

    """
    ls = [node_d for node_id, node_d in g[
        'infrastructure_graph'
    ].nodes_iter(data=True) if 'name' in node_d]  # Exclude fake nodes

    # Save
    target_folder = g['target_folder']
    summary_folder = make_folder(join(target_folder, 'summary'))
    save_summary(summary_folder, ls, g, VARIABLE_NAMES)

    # Prepare summaries
    d = OrderedDict()
    graph = g['infrastructure_graph']
    # TODO: Use JSON after we convert pandas series into dictionaries
    write_gpickle(graph, join(target_folder, 'infrastructure_graph.pkl'))

    # Map
    technologies = g['selected_technologies']
    color_by_technology = {
        technology: COLORS[i] for i, technology in enumerate(technologies)
    }
    columns = [
        'Name',
        'Peak Demand (kW)',
        'Proposed MV Line Length (m)',
        'Proposed Technology',
        'Levelized Cost Per kWh Consumed',
        'Connection Order',
        'WKT',
        'FillColor',
        'RadiusInPixelsRange5-10',
    ]
    rows = []
    for node_id, node_d in graph.nodes_iter(data=True):
        if 'name' not in node_d:
            continue  # Exclude fake nodes
        longitude, latitude = node_d['longitude'], node_d['latitude']
        technology = node_d['proposed_technology']
        rows.append({
            'Name': node_d['name'],
            'Peak Demand (kW)': node_d['peak_demand_in_kw'],
            'Proposed MV Line Length (m)': node_d[
                'grid_mv_line_adjusted_length_in_meters'],
            'Proposed Technology': format_technology(technology),
            'Levelized Cost Per kWh Consumed': node_d[
                technology + '_local_levelized_cost_per_kwh_consumed'],
            'Connection Order': node_d.get('order', ''),
            'WKT': Point(latitude, longitude).wkt,
            'FillColor': color_by_technology[technology],
            'RadiusInPixelsRange5-10': node_d['peak_demand_in_kw'],
        })
    for node1_id, node2_id, edge_d in graph.edges_iter(data=True):
        node1_d, node2_d = graph.node[node1_id], graph.node[node2_id]
        name = 'From %s to %s' % (
            node1_d.get('name', 'the grid'),
            node2_d.get('name', 'the grid'))
        peak_demand = max(
            node1_d['peak_demand_in_kw'],
            node2_d['peak_demand_in_kw'])
        line_length = edge_d['grid_mv_line_adjusted_length_in_meters']
        geometry_wkt = LineString([
            (node1_d['latitude'], node1_d['longitude']),
            (node2_d['latitude'], node2_d['longitude']),
        ])
        rows.append({
            'Name': name,
            'Peak Demand (kW)': peak_demand,
            'Proposed MV Line Length (m)': line_length,
            'Proposed Technology': 'Grid',
            'WKT': geometry_wkt,
            'FillColor': color_by_technology['grid'],
        })
    if 'grid_mv_line_geotable' in g:
        for geometry_wkt in g['grid_mv_line_geotable']['wkt']:
            rows.append({
                'Name': '(Existing MV Line)',
                'Proposed Technology': 'grid',
                'WKT': geometry_wkt,
                'FillColor': color_by_technology['grid'],
            })
    infrastructure_geotable_path = join(
        target_folder, 'infrastructure_map.csv')
    DataFrame(rows)[columns].to_csv(infrastructure_geotable_path, index=False)
    d['infrastructure_streets_satellite_geotable_path'] = \
        infrastructure_geotable_path

    # Show executive summary
    keys = [
        'discounted_cost_by_technology',
        'levelized_cost_by_technology',
        'count_by_technology',
    ]
    table = concat((Series(g[key]) for key in keys), axis=1)
    table.index.name = 'Technology'
    table.index = [format_technology(x) for x in table.index]
    table.columns = [
        'Discounted Cost', 'Levelized Cost Per kWh Consumed', 'Count']
    table_path = join(target_folder, 'executive_summary.csv')
    table.to_csv(table_path)
    d['executive_summary_table_path'] = table_path
    # Show edge summary
    rows = []
    for node1_id, node2_id, edge_d in graph.edges_iter(data=True):
        node1_d = graph.node[node1_id]
        node2_d = graph.node[node2_id]
        name = 'From %s to %s' % (
            node1_d.get('name', 'the grid'),
            node2_d.get('name', 'the grid'))
        line_length = edge_d['grid_mv_line_adjusted_length_in_meters']
        discounted_cost = edge_d['grid_mv_line_discounted_cost']
        rows.append([name, line_length, discounted_cost])
    table_path = join(target_folder, 'grid_mv_line.csv')
    DataFrame(rows, columns=[
        'Name', 'Length (m)', 'Discounted Cost']).sort_values(
        'Length (m)',
    ).to_csv(table_path, index=False)
    d['grid_mv_line_table_path'] = table_path
    # Show node summary
    rows = []
    for node_id, node_d in graph.nodes_iter(data=True):
        if 'name' not in node_d:
            continue  # We have a fake node
        columns = [node_d['name'], node_d.get('order', '')]
        columns.extend(node_d[
            x + '_local_levelized_cost_per_kwh_consumed'
        ] for x in technologies)
        columns.append(format_technology(node_d['proposed_technology']))
        rows.append(columns)
    table_path = join(target_folder, 'levelized_cost_by_technology.csv')
    DataFrame(rows, columns=[
        'Name', 'Connection Order',
    ] + [
        format_technology(x) for x in technologies
    ] + ['Proposed Technology']).sort_values(
        'Connection Order',
    ).to_csv(table_path, index=False)
    d['levelized_cost_by_technology_table_path'] = table_path

    return d
    """


def save_summary(target_folder, ls, g, variable_names):
    keys = []
    for x in g['demand_point_table'].columns:
        if x in variable_names:
            continue
        keys.append(x)
    if len(keys) > 1:
        keys.append('')
    for x in variable_names:
        keys.append(x)
    table = get_table_from_variables(ls, g, keys)
    table.to_csv(join(target_folder, 'costs.csv'))
    example_table = table.reset_index().groupby(
        'proposed technology').first().reset_index().transpose()
    example_table.to_csv(join(target_folder, 'examples.csv'), header=False)


def compute(f, l, g=None, prefix=''):
    'Compute the function using local arguments if possible'
    value_by_key = rename_keys(compute_raw(f, l, g), prefix=prefix)
    local_overrides = l.get('local_overrides', {})
    for key in local_overrides:
        local_value = local_overrides[key]
        if isnull(local_value):
            continue
        if key in value_by_key:
            value_by_key[key] = local_value
    return value_by_key


def compute_raw(f, l, g=None):
    if not g:
        g = {}
    # If the function wants every argument, provide every argument
    argument_specification = inspect.getargspec(f)
    if argument_specification.keywords:
        return f(**merge_dictionaries(g, l))
    # Otherwise, provide only requested arguments
    keywords = {}
    for argument_name in argument_specification.args:
        argument_value = l.get(argument_name, g.get(argument_name))
        if argument_value is None:
            raise ValidationError(argument_name, 'required')
        keywords[argument_name] = argument_value
    return f(**keywords)


def get_by_prefix(value_by_key, prefix):
    for key in value_by_key:
        if key.startswith(prefix):
            return value_by_key[key]


def get_graph_from_table(table):
    graph = Graph()
    for index, row in table.iterrows():
        graph.add_node(index, dict(row))
    return graph


def get_table_from_graph(graph, keys=None):
    index, rows = zip(*graph.nodes_iter(data=True))
    if keys:
        rows = ({k: d[k] for k in keys} for d in rows)
    return DataFrame(rows, index=index)


def get_table_from_variables(ls, g, keys):
    rows = [[l.get(x, g.get(x, '')) for x in keys] for l in ls]
    # Encourage spreadsheet programs to include empty columns when sorting rows
    columns = [x.replace('_', ' ') or '-' for x in keys]
    return DataFrame(rows, columns=columns).set_index('name')


def interpolate_values(source_table, target_column, target_value):
    t = source_table
    assert len(t) > 0
    assert len(t) == len(set(t[target_column]))
    # Get indices of two rows nearest to target value
    difference = t[target_column] - target_value
    sorted_indices = difference.abs().argsort()
    index0 = sorted_indices[0]
    index1 = sorted_indices[1] if len(sorted_indices) > 1 else index0
    # Compute fraction of difference in target column
    fraction = divide_safely(
        t[target_column].ix[index0],
        t[target_column].ix[index1],
        ExpectedPositive(target_column))
    # Interpolate
    return t.ix[index0] + (t.ix[index1] - t.ix[index0]) * fraction


def rename_keys(value_by_key, prefix='', suffix=''):
    d = {}
    for key, value in value_by_key.items():
        if prefix and not key.startswith(prefix):
            key = prefix + key
        if suffix and not key.endswith(suffix):
            key = key + suffix
        d[key] = value
    return d


def format_technology(x):
    return x.replace('_', ' ').title()


def _get_argument_file_name(k, v):
    file_base = k
    file_base = file_base.replace('_geotable_path', 's')
    file_base = file_base.replace('_table_path', 's')
    file_base = file_base.replace('_text_path', '')
    file_base = file_base.replace('_path', '')
    file_extension = splitext(v)[1]
    return file_base.replace('_', '-') + file_extension
