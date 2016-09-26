import geometryIO
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
        for geometry in geometries:
            geometry.coords = [flip_xy(xyz) for xyz in geometry.coords]
        table = DataFrame(fields, columns=[x[0] for x in definitions])
        table['WKT'] = [x.wkt for x in geometries]
    else:
        raise UnsupportedFormat('cannot load geotable (%s)' % path)
    return table


def flip_xy(xyz):
    xyz = list(xyz)
    xyz[0], xyz[1] = xyz[1], xyz[0]
    return xyz
