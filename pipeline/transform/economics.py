from __future__ import annotations

from pipeline.config import DEFAULT_LOAD_FACTOR
from pipeline.ingest.aircraft_perf import SubsonicAircraft, SupersonicAircraft, trips_per_day


def route_economics(route_score: dict, supersonic: SupersonicAircraft, subsonic: SubsonicAircraft) -> dict:
    """
    Estimate flight-level and annual economics for a daily Overture operation with blended fuel burn.
    """
    distance_nm = route_score["distance_nm"]
    load_factor = DEFAULT_LOAD_FACTOR
    pax_per_flight = supersonic.pax_capacity * load_factor
    revenue_per_flight = pax_per_flight * route_score["business_fare_est"]
    total_fuel_kg = (
        route_score["overwater_cruise_hr"] * supersonic.fuel_burn_supersonic_hr_kg
        + route_score["boomless_cruise_hr"] * supersonic.fuel_burn_boomless_hr_kg
        + route_score["subsonic_phase_hr"] * supersonic.fuel_burn_subsonic_hr_kg
    )
    fuel_cost = total_fuel_kg * supersonic.fuel_price_per_kg_usd
    non_fuel_cost = supersonic.non_fuel_casm_cents / 100 * distance_nm * supersonic.pax_capacity
    cost_per_flight = fuel_cost + non_fuel_cost
    profit_per_flight = revenue_per_flight - cost_per_flight
    flights_per_day = trips_per_day(distance_nm, supersonic, overwater_pct=route_score["overwater_pct"]) * 2
    annual_flights = flights_per_day * 365
    annual_revenue = annual_flights * revenue_per_flight
    annual_cost = annual_flights * cost_per_flight
    annual_profit = annual_revenue - annual_cost
    breakeven_load_factor = cost_per_flight / (route_score["business_fare_est"] * supersonic.pax_capacity)
    payback_years = supersonic.aircraft_price_M * 1_000_000 / max(annual_profit, 1)
    fuel_per_hr = total_fuel_kg / max(route_score["supersonic_block_hr"], 1e-6)
    return {
        "revenue_per_flight": round(revenue_per_flight, 0),
        "cost_per_flight": round(cost_per_flight, 0),
        "profit_per_flight": round(profit_per_flight, 0),
        "annual_revenue_M": round(annual_revenue / 1_000_000, 2),
        "annual_cost_M": round(annual_cost / 1_000_000, 2),
        "annual_profit_M": round(annual_profit / 1_000_000, 2),
        "payback_years": round(payback_years, 1 if payback_years < 100 else 0),
        "breakeven_load_factor": round(breakeven_load_factor, 3),
        "flights_per_day": round(flights_per_day, 1),
        "fuel_cost_per_flight": round(fuel_cost, 0),
        "non_fuel_cost_per_flight": round(non_fuel_cost, 0),
        "fuel_per_hr": round(fuel_per_hr, 0),
        "total_fuel_kg": round(total_fuel_kg, 0),
    }
