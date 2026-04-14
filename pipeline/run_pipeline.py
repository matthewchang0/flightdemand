from __future__ import annotations

import logging

import pandas as pd

from pipeline.config import (
    EUROSTAT_PATH,
    OUTPUT_DATA_DIR,
    TOP_CANDIDATE_LIMIT,
    ensure_directories,
)
from pipeline.ingest.aircraft_perf import SubsonicAircraft, SupersonicAircraft
from pipeline.ingest.airports import load_airports
from pipeline.ingest.business_index import get_bti
from pipeline.ingest.fares import classify_region, estimate_premium_fare
from pipeline.ingest.traffic import (
    calibrate_gravity_model,
    estimate_traffic_no_bts,
    load_airport_throughput,
    load_bts_t100,
    load_eurostat,
)
from pipeline.output.export import export_results
from pipeline.output.ranker import rank_routes
from pipeline.transform.demand_scorer import generate_route_thesis, score_route
from pipeline.transform.economics import route_economics
from pipeline.transform.overwater_check import compute_overwater_pct, load_land_polygons
from pipeline.transform.route_builder import build_candidate_routes
from pipeline.transform.time_savings import compute_time_savings

LOGGER = logging.getLogger("supersonic-demand")


def _merge_traffic_sources(bts: pd.DataFrame, eurostat: pd.DataFrame) -> pd.DataFrame:
    combined = pd.concat([bts, eurostat], ignore_index=True)
    if combined.empty:
        return combined
    aggregated = (
        combined.groupby(["origin_iata", "dest_iata"], as_index=False)
        .agg(
            annual_pax=("annual_pax", "sum"),
            annual_departures=("annual_departures", "sum"),
            avg_seats_per_flight=("avg_seats_per_flight", "mean"),
        )
        .reset_index(drop=True)
    )
    return aggregated


def _select_strategic_airports(airports: pd.DataFrame, throughput: pd.DataFrame, traffic: pd.DataFrame) -> pd.DataFrame:
    throughput_lookup = throughput.set_index("iata")["total_pax_millions"].to_dict()
    observed_airports: set[str] = set()
    if not traffic.empty:
        observed_airports = set(traffic["origin_iata"]).union(set(traffic["dest_iata"]))
    strategic = airports.loc[
        airports["iata"].isin(observed_airports)
        | (airports["iata"].map(throughput_lookup).fillna(0) >= 15.0)
    ].copy()
    return strategic.reset_index(drop=True)


def _attach_observed_traffic(routes: pd.DataFrame, traffic: pd.DataFrame) -> pd.DataFrame:
    if traffic.empty:
        routes["annual_pax"] = pd.NA
        routes["traffic_source"] = "gravity_model"
        return routes
    return routes.merge(traffic[["origin_iata", "dest_iata", "annual_pax"]], on=["origin_iata", "dest_iata"], how="left")


def _adjust_overwater_pct(raw_overwater_pct: float, region: str) -> float:
    if region == "transatlantic":
        return max(raw_overwater_pct, 0.85)
    if region == "transpacific":
        return max(raw_overwater_pct, 0.9)
    return raw_overwater_pct


def build_ranked_routes() -> tuple[list[dict], dict]:
    ensure_directories()
    LOGGER.info("Loading airport metadata")
    airports = load_airports()
    LOGGER.info("Loaded %s large airports", len(airports))

    LOGGER.info("Loading traffic datasets")
    bts = load_bts_t100()
    eurostat = load_eurostat(EUROSTAT_PATH)
    traffic = _merge_traffic_sources(bts, eurostat)
    throughput = load_airport_throughput()
    airports = _select_strategic_airports(airports, throughput, traffic)
    LOGGER.info("Scoped to %s strategic large airports", len(airports))

    LOGGER.info("Building candidate routes")
    candidate_routes = build_candidate_routes(airports)
    LOGGER.info("Built %s raw candidate routes", len(candidate_routes))
    candidate_routes = _attach_observed_traffic(candidate_routes, traffic)

    gravity_training = candidate_routes.dropna(subset=["annual_pax"]).copy()
    gravity_params = calibrate_gravity_model(gravity_training, throughput)
    LOGGER.info(
        "Gravity model calibrated: K=%.6f alpha=%.2f beta=%.2f gamma=%.2f R2=%.2f",
        gravity_params["K"],
        gravity_params["alpha"],
        gravity_params["beta"],
        gravity_params["gamma"],
        gravity_params["r2"],
    )

    throughput_lookup = throughput.set_index("iata")["total_pax_millions"].to_dict()
    quick_scores = []
    for route in candidate_routes.to_dict("records"):
        origin_throughput = throughput_lookup.get(route["origin_iata"], 10.0)
        dest_throughput = throughput_lookup.get(route["dest_iata"], 10.0)
        avg_bti = (get_bti(route["origin_city"]) + get_bti(route["dest_city"])) / 2
        observed = route.get("annual_pax")
        proxy_pax = observed if pd.notna(observed) else ((origin_throughput * dest_throughput) ** 0.5) * 25_000
        quick_scores.append(proxy_pax * avg_bti)
    candidate_routes["quick_score"] = quick_scores
    candidate_routes = (
        candidate_routes.sort_values("quick_score", ascending=False).head(TOP_CANDIDATE_LIMIT).reset_index(drop=True)
    )
    LOGGER.info("Pruned to %s high-potential routes for detailed scoring", len(candidate_routes))

    LOGGER.info("Loading coastline geometry")
    land_polygons = load_land_polygons()

    supersonic = SupersonicAircraft()
    subsonic = SubsonicAircraft()
    detailed_routes: list[dict] = []

    for route in candidate_routes.to_dict("records"):
        if pd.isna(route.get("annual_pax")):
            estimated_traffic = estimate_traffic_no_bts(route, route, throughput, params=gravity_params)
            route["annual_pax"] = estimated_traffic
            route["traffic_source"] = "gravity_model"
        else:
            route["traffic_source"] = "observed"

        raw_overwater_pct = compute_overwater_pct(
            route["origin_lat"],
            route["origin_lon"],
            route["dest_lat"],
            route["dest_lon"],
            land_polygons,
        )
        region = classify_region(route["origin_country_code"], route["dest_country_code"])
        overwater_pct = _adjust_overwater_pct(raw_overwater_pct, region)
        time_savings = compute_time_savings(route["distance_nm"], overwater_pct, supersonic, subsonic)
        fare_estimate = estimate_premium_fare(route["distance_nm"], region)
        route["route_region"] = region
        route["overwater_pct"] = overwater_pct
        route["time_saved_hr"] = time_savings["time_saved_hr"]
        route["bti_origin"] = get_bti(route["origin_city"])
        route["bti_dest"] = get_bti(route["dest_city"])
        detailed_routes.append({**route, **time_savings, **fare_estimate})

    max_pax = max(route["annual_pax"] for route in detailed_routes)
    revenue_candidates = [route["annual_pax"] * 0.15 * 0.30 * route["business_fare"] for route in detailed_routes]
    max_revenue = max(revenue_candidates)

    scored_routes: list[dict] = []
    for route in detailed_routes:
        route_score = score_route(
            route=route,
            traffic=route["annual_pax"],
            bti_origin=route["bti_origin"],
            bti_dest=route["bti_dest"],
            time_savings=route,
            overwater_pct=route["overwater_pct"],
            fare_estimate={"business_fare": route["business_fare"], "first_fare": route["first_fare"]},
            max_pax=max_pax,
            max_revenue=max_revenue,
        )
        route_score.update(route_economics(route_score, supersonic, subsonic))
        scored_routes.append(route_score)

    ranked = rank_routes(scored_routes)
    for route in ranked:
        route["why_this_route"] = generate_route_thesis(route)
    summary = export_results(ranked, OUTPUT_DATA_DIR, analyzed_count=len(scored_routes))
    return ranked, summary


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    ranked, summary = build_ranked_routes()
    LOGGER.info("Exported %s ranked routes", len(ranked))
    print(pd.DataFrame(ranked)[["rank", "origin_iata", "dest_iata", "total_score", "tier"]].head(10).to_string(index=False))
    print()
    print(summary)


if __name__ == "__main__":
    main()
