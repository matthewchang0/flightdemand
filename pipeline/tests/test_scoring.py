from pipeline.transform.demand_scorer import route_viability_score, score_route


def test_score_range():
    score = __sample_score(overwater_pct=0.95)
    assert 0 <= score["total_score"] <= 100


def test_jfk_lhr_top_tier():
    score = __sample_score(overwater_pct=0.97)
    assert score["total_score"] >= 75


def test_overland_routes_score_meaningfully():
    score = __sample_score(overwater_pct=0.0)
    assert score["total_score"] >= 50


def test_viability_score_overland_not_zero():
    assert route_viability_score(0.0) >= 7.0


def test_score_components_sum():
    score = __sample_score(overwater_pct=0.85)
    total = (
        score["traffic_score"]
        + score["premium_demand_score"]
        + score["time_savings_score"]
        + score["viability_score"]
        + score["revenue_score"]
    )
    assert round(total, 2) == score["total_score"]


def __sample_score(overwater_pct: float):
    return score_route(
        route={"origin_iata": "JFK", "dest_iata": "LHR", "distance_nm": 2991, "traffic_source": "observed"},
        traffic=4_200_000,
        bti_origin=98,
        bti_dest=95,
        time_savings={
            "supersonic_block_hr": 3.3,
            "subsonic_block_hr": 6.9,
            "time_saved_hr": 3.6 if overwater_pct else 1.4,
            "time_saved_pct": 0.52 if overwater_pct else 0.24,
            "effective_speed_kts": 900 if overwater_pct else 660,
            "overwater_cruise_hr": 2.8 if overwater_pct else 0.0,
            "boomless_cruise_hr": 0.3 if overwater_pct else 3.5,
            "subsonic_phase_hr": 0.5,
            "overture_without_boomless_block_hr": 5.4 if not overwater_pct else 3.5,
            "boomless_savings_min": 82 if not overwater_pct else 8,
        },
        overwater_pct=overwater_pct,
        fare_estimate={"business_fare": 3600, "first_fare": 6480},
        max_pax=4_500_000,
        max_revenue=700_000_000,
    )
