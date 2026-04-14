from __future__ import annotations

from itertools import combinations
from math import atan2, cos, radians, sin, sqrt

import pandas as pd

from pipeline.config import MAX_ROUTE_DISTANCE_NM, MIN_ROUTE_DISTANCE_NM, SOFT_MAX_ROUTE_DISTANCE_NM

EARTH_RADIUS_NM = 3440.065


def haversine_nm(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    lat1_rad, lon1_rad = radians(lat1), radians(lon1)
    lat2_rad, lon2_rad = radians(lat2), radians(lon2)
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    a = sin(dlat / 2) ** 2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return EARTH_RADIUS_NM * c


def initial_bearing_deg(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    lat1_rad, lon1_rad = radians(lat1), radians(lon1)
    lat2_rad, lon2_rad = radians(lat2), radians(lon2)
    dlon = lon2_rad - lon1_rad
    x = sin(dlon) * cos(lat2_rad)
    y = cos(lat1_rad) * sin(lat2_rad) - sin(lat1_rad) * cos(lat2_rad) * cos(dlon)
    bearing = atan2(x, y)
    return (bearing * 180 / 3.141592653589793 + 360) % 360


def build_candidate_routes(airports: pd.DataFrame) -> pd.DataFrame:
    """
    Generate unique strategic candidate airport pairs in the target distance band.
    """
    records: list[dict] = []
    airport_rows = airports.to_dict("records")
    for origin, dest in combinations(airport_rows, 2):
        first, second = sorted((origin, dest), key=lambda airport: airport["iata"])
        distance_nm = haversine_nm(origin["lat"], origin["lon"], dest["lat"], dest["lon"])
        if distance_nm < MIN_ROUTE_DISTANCE_NM or distance_nm > SOFT_MAX_ROUTE_DISTANCE_NM:
            continue
        records.append(
            {
                "origin_iata": first["iata"],
                "dest_iata": second["iata"],
                "origin_city": first["city"],
                "dest_city": second["city"],
                "origin_country": first["country"],
                "dest_country": second["country"],
                "origin_country_code": first["country_code"],
                "dest_country_code": second["country_code"],
                "origin_lat": first["lat"],
                "origin_lon": first["lon"],
                "dest_lat": second["lat"],
                "dest_lon": second["lon"],
                "distance_nm": round(distance_nm, 1),
                "bearing_deg": round(initial_bearing_deg(first["lat"], first["lon"], second["lat"], second["lon"]), 1),
                "range_limited": distance_nm > MAX_ROUTE_DISTANCE_NM,
            }
        )
    return pd.DataFrame.from_records(records)
