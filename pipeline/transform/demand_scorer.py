from __future__ import annotations

from math import log

from pipeline.config import PREMIUM_PAX_SHARE, SUPERSONIC_CAPTURE_RATE


def classify_route_type(overwater_pct: float) -> str:
    if overwater_pct >= 0.8:
        return "overwater"
    if overwater_pct >= 0.2:
        return "hybrid"
    return "overland"


def viability_score(overwater_pct: float) -> float:
    return 8.0 + 7.0 * overwater_pct


def route_viability_score(overwater_pct: float) -> float:
    return viability_score(overwater_pct)


def compute_time_savings_score(time_saved_hr: float, time_saved_pct: float) -> float:
    return 12.5 * min(1, time_saved_hr / 4.0) + 12.5 * min(1, time_saved_pct / 0.55)


def score_route(
    route: dict,
    traffic: float,
    bti_origin: float,
    bti_dest: float,
    time_savings: dict,
    overwater_pct: float,
    fare_estimate: dict,
    max_pax: float,
    max_revenue: float,
    max_bti: float = 100.0,
) -> dict:
    traffic_score = 25 * (log(traffic + 1) / log(max_pax + 1)) if max_pax else 0.0
    premium_demand_score = 20 * (bti_origin + bti_dest) / (2 * max_bti)
    time_savings_score = compute_time_savings_score(time_savings["time_saved_hr"], time_savings["time_saved_pct"])
    viability_component = viability_score(overwater_pct)
    estimated_premium_pax = traffic * PREMIUM_PAX_SHARE
    estimated_supersonic_pax = estimated_premium_pax * SUPERSONIC_CAPTURE_RATE
    estimated_revenue = estimated_supersonic_pax * fare_estimate["business_fare"]
    revenue_score = 15 * (log(estimated_revenue + 1) / log(max_revenue + 1)) if max_revenue else 0.0
    if route["traffic_source"] != "observed":
        traffic_score *= 0.85
        revenue_score *= 0.85
    min_bti = min(bti_origin, bti_dest)
    if min_bti < 50:
        traffic_score *= 0.7
        premium_demand_score *= 0.75
        revenue_score *= 0.7
    elif min_bti < 60:
        traffic_score *= 0.78
        premium_demand_score *= 0.82
        revenue_score *= 0.78
    elif min_bti < 70:
        traffic_score *= 0.88
        premium_demand_score *= 0.9
        revenue_score *= 0.88

    traffic_score = round(traffic_score, 2)
    premium_demand_score = round(premium_demand_score, 2)
    time_savings_score = round(time_savings_score, 2)
    viability_component = round(viability_component, 2)
    revenue_score = round(revenue_score, 2)
    total_score = round(
        traffic_score + premium_demand_score + time_savings_score + viability_component + revenue_score,
        2,
    )
    return {
        **route,
        "total_score": total_score,
        "traffic_score": traffic_score,
        "premium_demand_score": premium_demand_score,
        "time_savings_score": time_savings_score,
        "viability_score": viability_component,
        "revenue_score": revenue_score,
        "annual_pax": int(round(traffic)),
        "estimated_premium_pax": int(round(estimated_premium_pax)),
        "estimated_supersonic_revenue_M": round(estimated_revenue / 1_000_000, 2),
        "business_fare_est": fare_estimate["business_fare"],
        "first_fare_est": fare_estimate["first_fare"],
        "bti_origin": round(bti_origin, 1),
        "bti_dest": round(bti_dest, 1),
        "overwater_pct": round(overwater_pct, 4),
        "route_type": classify_route_type(overwater_pct),
        "traffic_source": route["traffic_source"],
        **time_savings,
    }


def generate_route_thesis(route_score: dict) -> str:
    if route_score["route_type"] == "overland":
        return (
            f'{route_score["origin_iata"]}-{route_score["dest_iata"]} ranks #{route_score["rank"]} as a Boomless Cruise route, '
            f'flying at Mach 1.15 over land to save {route_score["time_saved_hr"]:.1f} hours. '
            f'With {route_score["annual_pax"] / 1_000_000:.1f}M annual passengers and strong premium demand '
            f'(BTI {route_score["bti_origin"]:.0f}/{route_score["bti_dest"]:.0f}), it highlights the new overland opportunity unlocked by quiet supersonic operations.'
        )
    if route_score["route_type"] == "hybrid":
        return (
            f'{route_score["origin_iata"]}-{route_score["dest_iata"]} blends full Mach 1.7 overwater cruise with Boomless Cruise over land, '
            f'saving {route_score["time_saved_hr"]:.1f} hours across a {route_score["overwater_pct"] * 100:.0f}% overwater routing. '
            f'Its {route_score["annual_pax"] / 1_000_000:.1f}M annual passengers and BTI {route_score["bti_origin"]:.0f}/{route_score["bti_dest"]:.0f} endpoints make it a strong mixed-regime candidate.'
        )
    return (
        f'{route_score["origin_iata"]}-{route_score["dest_iata"]} ranks highly because it combines '
        f'{route_score["annual_pax"] / 1_000_000:.1f}M annual passengers, strong business demand '
        f'(BTI {route_score["bti_origin"]:.0f}/{route_score["bti_dest"]:.0f}), '
        f'{route_score["overwater_pct"] * 100:.0f}% overwater routing, and '
        f'{route_score["time_saved_hr"]:.1f} hours of block-time savings. '
        f'Estimated annual supersonic revenue potential is ${route_score["estimated_supersonic_revenue_M"]:.0f}M.'
    )
