import geometryIO
from invisibleroads_macros.geometry import flip_geometry_coordinates
from pandas import DataFrame, read_csv

from .exceptions import UnsupportedFormat


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
        # Convert to (longitude, latitude)
        geometries = [normalize_geometry(x) for x in geometries]
        # Convert to (latitude, longitude)
        flipped_geometries = flip_geometry_coordinates(geometries)
        table = DataFrame(fields, columns=[x[0] for x in definitions])
        table['WKT'] = [x.wkt for x in flipped_geometries]
    else:
        raise UnsupportedFormat('cannot load geotable (%s)' % path)
    return table
