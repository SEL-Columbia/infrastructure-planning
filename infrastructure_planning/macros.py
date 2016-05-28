import inspect
from collections import OrderedDict
from invisibleroads_macros.iterable import merge_dictionaries


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


def rename_keys(value_by_key, prefix='', suffix=''):
    d = OrderedDict()
    for key, value in value_by_key.items():
        if prefix and not key.startswith(prefix):
            key = prefix + key
        if suffix and not key.endswith(suffix):
            key = key + suffix
        d[key] = value
    return d
