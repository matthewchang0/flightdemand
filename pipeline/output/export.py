from __future__ import annotations

import json
import shutil
from pathlib import Path

import pandas as pd

from pipeline.config import REGION_GROUPS
from pipeline.config import DASHBOARD_ROUTES_PATH, DASHBOARD_SUMMARY_PATH


def infer_region(route: dict) -> str:
    origin = route["origin_country_code"]
    dest = route["dest_country_code"]
    if (origin in REGION_GROUPS["north_america"] and dest in REGION_GROUPS["europe"]) or (
        dest in REGION_GROUPS["north_america"] and origin in REGION_GROUPS["europe"]
    ):
        return "transatlantic"
    if (
        origin in REGION_GROUPS["north_america"] and dest in (REGION_GROUPS["asia"] | REGION_GROUPS["oceania"])
    ) or (
        dest in REGION_GROUPS["north_america"] and origin in (REGION_GROUPS["asia"] | REGION_GROUPS["oceania"])
    ):
        return "transpacific"
    if (origin in REGION_GROUPS["europe"] and dest in REGION_GROUPS["asia"]) or (
        dest in REGION_GROUPS["europe"] and origin in REGION_GROUPS["asia"]
    ):
        return "europe_asia"
    if origin in REGION_GROUPS["middle_east"] or dest in REGION_GROUPS["middle_east"]:
        return "middle_east"
    if {origin, dest}.issubset(REGION_GROUPS["north_america"] | REGION_GROUPS["latin_america"]):
        return "americas"
    return "intercontinental"


def export_results(ranked: list[dict], output_dir: str | Path, analyzed_count: int | None = None) -> dict:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    routes_json = output_path / "routes.json"
    routes_csv = output_path / "routes.csv"
    summary_json = output_path / "summary.json"

    for route in ranked:
        route["region"] = infer_region(route)

    with routes_json.open("w") as handle:
        json.dump(ranked, handle, indent=2)

    pd.DataFrame(ranked).to_csv(routes_csv, index=False)

    routes_by_tier: dict[str, int] = {}
    routes_by_region: dict[str, int] = {}
    routes_by_route_type: dict[str, int] = {}
    for route in ranked:
        routes_by_tier[route["tier"]] = routes_by_tier.get(route["tier"], 0) + 1
        routes_by_region[route["region"]] = routes_by_region.get(route["region"], 0) + 1
        routes_by_route_type[route["route_type"]] = routes_by_route_type.get(route["route_type"], 0) + 1

    summary = {
        "total_routes_analyzed": analyzed_count or len(ranked),
        "top_50_routes": [
            {
                "rank": route["rank"],
                "origin": route["origin_iata"],
                "dest": route["dest_iata"],
                "score": route["total_score"],
                "tier": route["tier"],
            }
            for route in ranked
        ],
        "routes_by_tier": routes_by_tier,
        "routes_by_region": routes_by_region,
        "routes_by_route_type": routes_by_route_type,
        "total_addressable_premium_pax": int(sum(route["estimated_premium_pax"] for route in ranked)),
        "total_addressable_revenue_B": round(
            sum(route["estimated_supersonic_revenue_M"] for route in ranked) / 1000,
            2,
        ),
        "avg_time_saved_hr": round(sum(route["time_saved_hr"] for route in ranked) / len(ranked), 2),
        "avg_overwater_pct": round(sum(route["overwater_pct"] for route in ranked) / len(ranked), 4),
        "avg_score": round(sum(route["total_score"] for route in ranked) / len(ranked), 2),
        "overland_routes_unlocked": sum(1 for route in ranked if route["route_type"] == "overland"),
    }
    with summary_json.open("w") as handle:
        json.dump(summary, handle, indent=2)

    DASHBOARD_ROUTES_PATH.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(routes_json, DASHBOARD_ROUTES_PATH)
    shutil.copyfile(summary_json, DASHBOARD_SUMMARY_PATH)
    return summary
