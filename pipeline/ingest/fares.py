from __future__ import annotations

from pipeline.config import FARE_YIELD_BANDS, REGION_GROUPS


def classify_region(origin_country_code: str, dest_country_code: str) -> str:
    origin = origin_country_code.upper()
    dest = dest_country_code.upper()

    if {origin, dest}.issubset(REGION_GROUPS["europe"]):
        return "intra_europe"
    if {origin, dest}.issubset(REGION_GROUPS["asia"]):
        return "intra_asia"
    if origin in REGION_GROUPS["north_america"] and dest in REGION_GROUPS["europe"]:
        return "transatlantic"
    if dest in REGION_GROUPS["north_america"] and origin in REGION_GROUPS["europe"]:
        return "transatlantic"
    if origin in REGION_GROUPS["north_america"] and dest in REGION_GROUPS["asia"]:
        return "transpacific"
    if dest in REGION_GROUPS["north_america"] and origin in REGION_GROUPS["asia"]:
        return "transpacific"
    if origin in REGION_GROUPS["middle_east"] or dest in REGION_GROUPS["middle_east"]:
        return "middle_east_long_haul"
    if origin in REGION_GROUPS["north_america"] or dest in REGION_GROUPS["north_america"]:
        return "americas_long_haul"
    return "default_long_haul"


def estimate_premium_fare(distance_nm: float, region: str) -> dict:
    """
    Estimate one-way business and first class fares using published yield bands.
    """
    distance_km = distance_nm * 1.852
    low, high = FARE_YIELD_BANDS.get(region, FARE_YIELD_BANDS["default_long_haul"])
    midpoint_yield = (low + high) / 2
    taper = max(0.6, 1.0 - 0.00005 * distance_km)
    business_fare = midpoint_yield * distance_km * taper
    first_fare = business_fare * 1.8
    return {
        "region": region,
        "yield_per_km": round(midpoint_yield * taper, 4),
        "business_fare": round(business_fare, 2),
        "first_fare": round(first_fare, 2),
    }

