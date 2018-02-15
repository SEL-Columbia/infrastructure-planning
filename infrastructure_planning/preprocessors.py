from geopy.distance import vincenty as get_distance
from invisibleroads_macros.geometry import (
    drop_z, flip_xy, transform_geometries)
from invisibleroads_macros.log import get_log
from pandas import isnull
from shapely import wkt
from shapely.geometry import GeometryCollection

from .exceptions import ValidationError


DEMAND_POINT_TABLE_COLUMNS = [
    'name',
    'latitude',
    'longitude',
    'population',
]
L = get_log(__name__)


def normalize_demand_point_table(demand_point_table):
    # Check that required columns exist
    for column in DEMAND_POINT_TABLE_COLUMNS:
        if column not in demand_point_table.columns:
            raise ValidationError(
                'demand_point_table', 'missing column (%s)' % column)
    # Check that required columns are not empty
    for column in DEMAND_POINT_TABLE_COLUMNS:
        for value in demand_point_table[column]:
            if not isnull(value):
                continue
            raise ValidationError(
                'demand_point_table', 'missing value (%s)' % column)
    # Rename year to population_year
    if 'year' in demand_point_table.columns:
        demand_point_table = demand_point_table.rename(columns={
            'year': 'population_year'})
    # Use most recent population_year if there are many population_years
    if 'population_year' in demand_point_table.columns:
        demand_point_table = demand_point_table.sort_values(
            'population_year').groupby('name').last().reset_index()
    return {'demand_point_table': demand_point_table}


def normalize_connection_type_table(connection_type_table):
    connection_type_table['connection_type'] = connection_type_table[
        'connection_type'].apply(lambda x: x.lower().replace(' ', '_'))
    return {'connection_type_table': connection_type_table}


def normalize_grid_mv_transformer_table(grid_mv_transformer_table):
    return normalize_capacity_table(
        'grid_mv_transformer_table', grid_mv_transformer_table,
        'capacity_in_kva')


def normalize_diesel_mini_grid_generator_table(
        diesel_mini_grid_generator_table):
    return normalize_capacity_table(
        'diesel_mini_grid_generator_table', diesel_mini_grid_generator_table,
        'capacity_in_kw')


def normalize_solar_home_panel_table(solar_home_panel_table):
    return normalize_capacity_table(
        'solar_home_panel_table', solar_home_panel_table,
        'capacity_in_kw')


def normalize_solar_mini_grid_panel_table(solar_mini_grid_panel_table):
    return normalize_capacity_table(
        'solar_mini_grid_panel_table', solar_mini_grid_panel_table,
        'capacity_in_kw')


def normalize_grid_mv_line_geotable(grid_mv_line_geotable, demand_point_table):
    'Make sure that grid mv lines use (longitude, latitude) coordinate order'
    raw_geometries = [wkt.loads(x) for x in grid_mv_line_geotable['wkt']]
    # Remove incompatible geometries
    geometries, xs = [], []
    for x, geometry in enumerate(raw_geometries):
        if geometry.type.endswith('LineString'):
            geometries.append(geometry)
        else:
            L.warn(
                'Ignoring incompatible geometry '
                'in grid_mv_line_geotable (%s)' % geometry.wkt)
            xs.append(x)
    grid_mv_line_geotable.drop(grid_mv_line_geotable.index[xs])
    # Remove elevation
    geometries = transform_geometries(geometries, drop_z)
    # Match coordinate order
    if geometries:
        regular = tuple(GeometryCollection(geometries).centroid.coords[0])[:2]
        flipped = regular[1], regular[0]
        reference = tuple(demand_point_table[['longitude', 'latitude']].mean())
        # If the flipped coordinates are closer,
        if get_distance(reference, flipped) < get_distance(reference, regular):
            # Flip coordinates to get (longitude, latitude) coordinate order
            geometries = transform_geometries(geometries, flip_xy)
    grid_mv_line_geotable['wkt'] = [x.wkt for x in geometries]
    return {'grid_mv_line_geotable': grid_mv_line_geotable}


def normalize_capacity_table(table_name, table, capacity_column):
    capacity_values = table[capacity_column].values
    # Check that we have at least one row
    if not len(capacity_values):
        raise ValidationError(table_name, 'need at least one row')
    # Check that we do not have duplicate capacity values
    if len(capacity_values) != len(set(capacity_values)):
        raise ValidationError(table_name, 'remove duplicate capacity values')
    # Sort table by ascending capacity
    return {table_name: table.sort_values(capacity_column)}
