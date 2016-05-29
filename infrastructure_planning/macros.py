import inspect
from collections import OrderedDict
from invisibleroads_macros.iterable import merge_dictionaries
from networkx import Graph
from pandas import DataFrame


def compute(f, l, g=None):
    'Compute the function using local arguments if possible'
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
            raise KeyError(argument_name)
        keywords[argument_name] = argument_value
    return f(**keywords)


def get_by_prefix(value_by_key, prefix):
    for key, value in value_by_key.items():
        if key.startswith(prefix):
            return value


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
    return DataFrame(rows, columns=keys).set_index('name')


def rename_keys(value_by_key, prefix='', suffix=''):
    d = OrderedDict()
    for key, value in value_by_key.items():
        if prefix and not key.startswith(prefix):
            key = prefix + key
        if suffix and not key.endswith(suffix):
            key = key + suffix
        d[key] = value
    return d
