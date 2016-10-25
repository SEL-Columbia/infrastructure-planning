import csv
import geometryIO
import inspect
import simplejson as json
import shutil
from invisibleroads_macros.configuration import TerseArgumentParser
from invisibleroads_macros.disk import make_enumerated_folder_for, make_folder
from invisibleroads_macros.geometry import flip_geometry_coordinates
from invisibleroads_macros.iterable import merge_dictionaries
from invisibleroads_macros.math import divide_safely
from invisibleroads_macros.table import normalize_column_name
from networkx import Graph
from os.path import isabs, join, splitext
from pandas import DataFrame, isnull
from shapely import wkt

from .exceptions import (
    ExpectedPositive, InfrastructurePlanningError, ValidationError)
from .parsers import load_files


class BasicArgumentParser(TerseArgumentParser):

    def __init__(self, *args, **kw):
        super(BasicArgumentParser, self).__init__(*args, **kw)
        self.add_argument(
            'configuration_path', metavar='CONFIGURATION_PATH', nargs='?')
        self.add_argument('-w', '--source_folder', metavar='FOLDER')
        self.add_argument('-o', '--target_folder', metavar='FOLDER')


class InfrastructureGraph(Graph):

    def cycle_nodes(self):
        for node_id, node_d in self.nodes_iter(data=True):
            if 'name' not in node_d:
                continue  # We have a fake node
            yield node_id, node_d

    def cycle_edges(self):
        for node1_id, node2_id, edge_d in self.edges_iter(data=True):
            yield node1_id, node2_id, edge_d


def load_and_run(normalization_functions, main_functions, argument_parser):
    args = argument_parser.parse_args()
    g = load_arguments(args.__dict__)
    save_arguments(g, __file__)
    try:
        g = load_files(g)
        g = normalize_arguments(normalization_functions, g)
        run(main_functions, g)
    except InfrastructurePlanningError as e:
        exit(e)


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
    # Save global arguments as JSON
    json.dump(d, open(join(arguments_folder, 'arguments.json'), 'w'))
    # Save global arguments as CSV
    csv_writer = csv.writer(open(join(arguments_folder, 'arguments.csv'), 'w'))
    for x in d.items():
        csv_writer.writerow(x)


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
        for node_id, node_d in g['infrastructure_graph'].cycle_nodes():
            l = merge_dictionaries(node_d, {
                'node_id': node_id,
                'local_overrides': dict(g['demand_point_table'].ix[node_id])})
            node_d.update(compute(f, l, g))
    return g


def save_shapefile(target_path, geotable):
    # TODO: Save extra attributes
    geometries = [wkt.loads(x) for x in geotable['wkt']]
    # Shapefiles expect (x, y) or (longitude, latitude) coordinate order
    flipped_geometries = flip_geometry_coordinates(geometries)
    geometryIO.save(target_path, geometryIO.proj4LL, flipped_geometries)
    return target_path


def compute(f, l, g=None, prefix=''):
    'Compute the function using local arguments if possible'
    value_by_key = rename_keys(compute_raw(f, l, g) or {}, prefix=prefix)
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


def get_final_value(value_by_year):
    return value_by_year.ix[sorted(value_by_year.index)[-1]]


def get_graph_from_table(table):
    graph = InfrastructureGraph()
    for index, row in table.iterrows():
        graph.add_node(index, dict(row))
    return graph


def get_table_from_graph(graph, keys=None):
    index, rows = zip(*graph.cycle_nodes())
    if keys:
        rows = ({k: d[k] for k in keys} for d in rows)
    return DataFrame(rows, index=index)


def get_table_from_variables(ls, g, keys):
    rows = [[l.get(x, g.get(x, '')) for x in keys] for l in ls]
    return DataFrame(rows, columns=keys).set_index('name')


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


def _get_argument_file_name(k, v):
    file_base = k
    file_base = file_base.replace('_path', '')
    file_extension = splitext(v)[1]
    return file_base.replace('_', '-') + file_extension
