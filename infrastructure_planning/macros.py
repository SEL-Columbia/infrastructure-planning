import inspect
from invisibleroads_macros.iterable import merge_dictionaries
from invisibleroads_macros.math import divide_safely
from networkx import Graph
from pandas import DataFrame, isnull

from .exceptions import ExpectedPositive, InfrastructurePlanningError


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
            raise InfrastructurePlanningError(
                argument_name,
                'missing required parameter (%s)' % argument_name)
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
