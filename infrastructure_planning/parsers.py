import geometryIO
import re
from invisibleroads_macros.iterable import merge_dictionaries
from pandas import DataFrame, read_csv

from .exceptions import ValidationError, UnsupportedFormat


def load_files(g):
    file_key_pattern = re.compile(r'(.*)_(\w+)_path')
    file_value_by_name = {}
    for k, v in g.items():
        try:
            key_base, key_type = file_key_pattern.match(k).groups()
        except AttributeError:
            continue
        try:
            if key_type == 'text':
                name = key_base
                value = load_text(v)
            elif key_type == 'table':
                name = key_base + '_table'
                value = load_table(v)
            elif key_type == 'geotable':
                name = key_base + '_geotable'
                value = load_geotable(v)
            else:
                continue
        except UnsupportedFormat as e:
            raise ValidationError(k, e)
        file_value_by_name[name] = value
    return merge_dictionaries(g, file_value_by_name)


def load_text(path):
    return open(path).read().split()


def load_table(path):
    return read_csv(path)


def load_geotable(path):
    if path.endswith('.csv'):
        table = read_csv(path)
    elif path.endswith('.zip'):
        proj4, geometries, fields, definitions = geometryIO.load(path)
        normalize_geometry = geometryIO.get_transformGeometry(proj4)
        geometries = [normalize_geometry(x) for x in geometries]
        table = DataFrame(fields, columns=[x[0] for x in definitions])
        table['WKT'] = [x.wkt for x in geometries]
    else:
        raise UnsupportedFormat('cannot load geotable (%s)' % path)
    return table
