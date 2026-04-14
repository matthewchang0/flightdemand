from __future__ import annotations

from dataclasses import dataclass
from math import floor

from pipeline.config import OVERTURE_RANGE_LIMIT_NM, TAXI_OVERHEAD_HR


@dataclass(frozen=True)
class SupersonicAircraft:
    """Boom Overture-style assumptions with Boomless Cruise."""

    name: str = "Overture"
    pax_capacity: int = 72
    cruise_mach_supersonic: float = 1.7
    cruise_mach_boomless: float = 1.15
    cruise_mach_boomless_max: float = 1.3
    cruise_alt_supersonic_ft: float = 60_000
    cruise_alt_boomless_ft: float = 55_000
    max_range_nm: float = OVERTURE_RANGE_LIMIT_NM
    casm_cents: float = 20.0
    non_fuel_casm_cents: float = 12.5
    block_speed_overwater_kts: float = 975
    block_speed_overland_kts: float = 660
    fuel_burn_supersonic_hr_kg: float = 4_500
    fuel_burn_boomless_hr_kg: float = 3_200
    fuel_burn_subsonic_hr_kg: float = 2_500
    fuel_price_per_kg_usd: float = 0.85
    turnaround_hr: float = 1.5
    daily_utilization_hr: float = 12.0
    aircraft_price_M: float = 200.0


@dataclass(frozen=True)
class SubsonicAircraft:
    """Representative 787-9 assumptions."""

    name: str = "787-9"
    pax_capacity: int = 296
    cruise_mach: float = 0.85
    cruise_alt_ft: float = 43_000
    max_range_nm: float = 7_530
    casm_cents: float = 8.5
    fuel_burn_per_hr_kg: float = 5_800
    block_speed_kts: float = 470
    turnaround_hr: float = 2.0
    daily_utilization_hr: float = 14.0
    aircraft_price_M: float = 300.0


def block_time(distance_nm: float, aircraft, overwater_pct: float = 1.0) -> float:
    """
    Blended block time for Overture and a single-speed block time for subsonic aircraft.
    """
    if isinstance(aircraft, SupersonicAircraft):
        overwater_nm = distance_nm * overwater_pct
        overland_nm = distance_nm * (1 - overwater_pct)
        cruise_time_hr = (overwater_nm / aircraft.block_speed_overwater_kts) + (
            overland_nm / aircraft.block_speed_overland_kts
        )
        return cruise_time_hr + TAXI_OVERHEAD_HR
    return distance_nm / aircraft.block_speed_kts + TAXI_OVERHEAD_HR


def trips_per_day(distance_nm: float, aircraft, overwater_pct: float = 1.0) -> float:
    """
    Estimate how many roundtrips per day a single aircraft can cover.
    """
    trip_time = 2 * block_time(distance_nm, aircraft, overwater_pct=overwater_pct) + 2 * aircraft.turnaround_hr
    trips = aircraft.daily_utilization_hr / trip_time
    return floor(trips * 2) / 2
