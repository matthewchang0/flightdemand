from __future__ import annotations

import json
from pathlib import Path

from pyproj import Geod
from shapely.geometry import Point, shape
from shapely.ops import unary_union

from pipeline.config import LAND_GEOJSON_PATH, OVERWATER_SAMPLE_INTERVAL_NM

GEOD = Geod(ellps="WGS84")


def load_land_polygons(filepath: Path | str = LAND_GEOJSON_PATH):
    with Path(filepath).open() as handle:
        data = json.load(handle)
    geometries = [shape(feature["geometry"]) for feature in data["features"]]
    return unary_union(geometries)


def compute_overwater_pct(
    origin_lat: float,
    origin_lon: float,
    dest_lat: float,
    dest_lon: float,
    land_polygons,
) -> float:
    """
    Sample a great-circle route and compute the share of points not over land.
    """
    _, _, distance_m = GEOD.inv(origin_lon, origin_lat, dest_lon, dest_lat)
    distance_nm = distance_m / 1852
    n_segments = max(2, int(distance_nm / OVERWATER_SAMPLE_INTERVAL_NM))
    interior_points = GEOD.npts(origin_lon, origin_lat, dest_lon, dest_lat, n_segments - 1)
    samples = [(origin_lon, origin_lat), *interior_points, (dest_lon, dest_lat)]
    over_land = 0
    for lon, lat in samples:
        if land_polygons.covers(Point(lon, lat)):
            over_land += 1
    pct = 1.0 - (over_land / len(samples))
    return round(max(0.0, min(1.0, pct)), 4)

