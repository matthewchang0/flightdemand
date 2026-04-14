from pipeline.ingest.aircraft_perf import SubsonicAircraft, SupersonicAircraft
from pipeline.run_pipeline import build_ranked_routes
from pipeline.transform.economics import route_economics


def test_revenue_positive():
    economics = route_economics(__sample_route(), SupersonicAircraft(), SubsonicAircraft())
    assert economics["profit_per_flight"] > 0


def test_payback_reasonable():
    economics = route_economics(__sample_route(), SupersonicAircraft(), SubsonicAircraft())
    assert economics["payback_years"] < 20


def test_breakeven_lf():
    economics = route_economics(__sample_route(), SupersonicAircraft(), SubsonicAircraft())
    assert economics["breakeven_load_factor"] < 1.0


def test_boomless_fuel_burn_lower_than_supersonic():
    overland = route_economics(__sample_route(overwater_pct=0.0), SupersonicAircraft(), SubsonicAircraft())
    overwater = route_economics(__sample_route(overwater_pct=1.0), SupersonicAircraft(), SubsonicAircraft())
    assert overland["fuel_per_hr"] < overwater["fuel_per_hr"]


def test_domestic_routes_in_top_50():
    ranked, _ = build_ranked_routes()
    domestic_us = [
        route
        for route in ranked[:50]
        if route["origin_country_code"] == "US" and route["dest_country_code"] == "US"
    ]
    assert len(domestic_us) >= 2


def __sample_route(overwater_pct: float = 0.97):
    return {
        "distance_nm": 2991,
        "business_fare_est": 3600,
        "overwater_pct": overwater_pct,
        "overwater_cruise_hr": 2.8 if overwater_pct else 0.0,
        "boomless_cruise_hr": 0.1 if overwater_pct else 4.0,
        "subsonic_phase_hr": 0.5,
        "supersonic_block_hr": 3.4 if overwater_pct else 4.5,
    }
