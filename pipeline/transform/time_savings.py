from __future__ import annotations

from pipeline.ingest.aircraft_perf import SubsonicAircraft, SupersonicAircraft

BLOCK_OVERHEAD_HR = 0.25


def estimate_water_land_transitions(overwater_pct: float) -> int:
    if 0.0 < overwater_pct < 1.0:
        return 2
    return 0


def compute_time_savings(
    distance_nm: float,
    overwater_pct: float,
    supersonic: SupersonicAircraft,
    subsonic: SubsonicAircraft,
) -> dict:
    """
    Three-speed route timing model with full supersonic over water and Boomless Cruise over land.
    """
    overwater_distance = distance_nm * overwater_pct
    overland_distance = distance_nm * (1 - overwater_pct)
    overwater_time_hr = overwater_distance / supersonic.block_speed_overwater_kts if overwater_distance else 0.0
    boomless_time_hr = overland_distance / supersonic.block_speed_overland_kts if overland_distance else 0.0
    n_transitions = estimate_water_land_transitions(overwater_pct)
    transition_overhead_hr = (n_transitions * 8) / 60
    subsonic_phase_hr = BLOCK_OVERHEAD_HR + transition_overhead_hr

    supersonic_block_hr = overwater_time_hr + boomless_time_hr + subsonic_phase_hr
    subsonic_block_hr = distance_nm / subsonic.block_speed_kts + 0.5
    overture_without_boomless_block_hr = overwater_time_hr + (
        overland_distance / subsonic.block_speed_kts if overland_distance else 0.0
    ) + subsonic_phase_hr
    time_saved_hr = max(0.0, subsonic_block_hr - supersonic_block_hr)
    time_saved_pct = time_saved_hr / subsonic_block_hr if subsonic_block_hr else 0.0
    effective_speed_kts = distance_nm / max(supersonic_block_hr - BLOCK_OVERHEAD_HR, 1e-6)
    boomless_savings_min = max(
        0.0,
        ((overland_distance / subsonic.block_speed_kts) if overland_distance else 0.0) - boomless_time_hr,
    ) * 60
    return {
        "supersonic_block_hr": round(supersonic_block_hr, 2),
        "subsonic_block_hr": round(subsonic_block_hr, 2),
        "time_saved_hr": round(time_saved_hr, 2),
        "time_saved_pct": round(time_saved_pct, 4),
        "effective_speed_kts": round(effective_speed_kts, 1),
        "overwater_cruise_hr": round(overwater_time_hr, 2),
        "boomless_cruise_hr": round(boomless_time_hr, 2),
        "subsonic_phase_hr": round(subsonic_phase_hr, 2),
        "overture_without_boomless_block_hr": round(overture_without_boomless_block_hr, 2),
        "boomless_savings_min": round(boomless_savings_min, 1),
    }
