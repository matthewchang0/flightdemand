from __future__ import annotations

from math import exp, log
from pathlib import Path

import numpy as np
import pandas as pd

from pipeline.config import (
    DEFAULT_CONNECTIVITY_FACTOR,
    DEFAULT_TRAFFIC_CEILING,
    DEFAULT_TRAFFIC_FLOOR,
    THROUGHPUT_PATH,
    T100_PATH,
    T100_SAMPLE_PATH,
)


def _canonical_route(origin: str, dest: str) -> tuple[str, str]:
    pair = sorted((origin.upper(), dest.upper()))
    return pair[0], pair[1]


def _aggregate_routes(
    frame: pd.DataFrame,
    origin_col: str,
    dest_col: str,
    pax_col: str,
    departures_col: str,
    seats_col: str,
) -> pd.DataFrame:
    working = frame.copy()
    working["origin_iata"] = working[origin_col].str.upper()
    working["dest_iata"] = working[dest_col].str.upper()
    canonical = working.apply(
        lambda row: pd.Series(_canonical_route(row["origin_iata"], row["dest_iata"])),
        axis=1,
    )
    working[["origin_iata", "dest_iata"]] = canonical
    aggregated = (
        working.groupby(["origin_iata", "dest_iata"], as_index=False)
        .agg(
            annual_pax=(pax_col, "sum"),
            annual_departures=(departures_col, "sum"),
            annual_seats=(seats_col, "sum"),
        )
        .reset_index(drop=True)
    )
    aggregated["avg_seats_per_flight"] = np.where(
        aggregated["annual_departures"] > 0,
        aggregated["annual_seats"] / aggregated["annual_departures"],
        0,
    )
    return aggregated


def load_bts_t100(filepath: Path | str = T100_PATH) -> pd.DataFrame:
    """
    Load BTS T-100 International Segment data or the bundled sample fallback.
    """
    source_path = Path(filepath)
    if not source_path.exists():
        source_path = T100_SAMPLE_PATH
    frame = pd.read_csv(source_path)
    latest_year = int(frame["YEAR"].max())
    filtered = frame.loc[frame["YEAR"] == latest_year].copy()
    return _aggregate_routes(
        filtered,
        origin_col="ORIGIN",
        dest_col="DEST",
        pax_col="PASSENGERS",
        departures_col="DEPARTURES_PERFORMED",
        seats_col="SEATS",
    )


def load_eurostat(filepath: Path | str) -> pd.DataFrame:
    """
    Parse a Eurostat airport-pair file when provided. Returns an empty frame if unavailable.
    """
    path = Path(filepath)
    if not path.exists():
        return pd.DataFrame(
            columns=["origin_iata", "dest_iata", "annual_pax", "annual_departures", "avg_seats_per_flight"]
        )

    if path.suffix.lower() == ".csv":
        frame = pd.read_csv(path)
    else:
        frame = pd.read_csv(path, sep="\t")

    normalized = {column.lower(): column for column in frame.columns}
    required = {"origin", "dest", "passengers", "year"}
    if required.issubset(normalized):
        latest_year = int(frame[normalized["year"]].max())
        filtered = frame.loc[frame[normalized["year"]] == latest_year].copy()
        filtered[normalized.setdefault("departures", normalized["passengers"])] = filtered.get(
            normalized.get("departures", ""),
            0,
        )
        filtered[normalized.setdefault("seats", normalized["passengers"])] = filtered.get(
            normalized.get("seats", ""),
            filtered[normalized["passengers"]],
        )
        return _aggregate_routes(
            filtered,
            origin_col=normalized["origin"],
            dest_col=normalized["dest"],
            pax_col=normalized["passengers"],
            departures_col=normalized.get("departures", normalized["passengers"]),
            seats_col=normalized.get("seats", normalized["passengers"]),
        )

    return pd.DataFrame(
        columns=["origin_iata", "dest_iata", "annual_pax", "annual_departures", "avg_seats_per_flight"]
    )


def load_airport_throughput(filepath: Path | str = THROUGHPUT_PATH) -> pd.DataFrame:
    return pd.read_csv(filepath)


def estimate_route_traffic(origin: pd.Series, dest: pd.Series, throughput: pd.DataFrame) -> float:
    """
    Connectivity-factor estimate for routes missing direct observed traffic.
    """
    throughput_lookup = throughput.set_index("iata")["total_pax_millions"].to_dict()
    origin_pax = throughput_lookup.get(origin["iata"], 10.0)
    dest_pax = throughput_lookup.get(dest["iata"], 10.0)
    distance_km = origin["distance_nm"] * 1.852
    base = np.sqrt(origin_pax * dest_pax) * 1_000_000
    distance_decay = exp(-distance_km / 8_000)
    estimated = base * distance_decay * DEFAULT_CONNECTIVITY_FACTOR
    return float(max(DEFAULT_TRAFFIC_FLOOR, min(DEFAULT_TRAFFIC_CEILING, estimated)))


def estimate_traffic_no_bts(
    origin: pd.Series,
    dest: pd.Series,
    throughput_df: pd.DataFrame,
    params: dict[str, float] | None = None,
) -> int:
    """
    Gravity model estimate calibrated against known routes where available.
    """
    params = params or {"K": 0.0005, "alpha": 0.7, "beta": 0.7, "gamma": 1.2}
    lookup = throughput_df.set_index("iata")["total_pax_millions"].to_dict()
    throughput_a = lookup.get(origin["origin_iata"], 12.0)
    throughput_b = lookup.get(dest["dest_iata"], 12.0)
    distance_km = max(origin["distance_nm"] * 1.852, 250.0)
    estimate = params["K"] * (throughput_a**params["alpha"]) * (throughput_b**params["beta"]) / (
        distance_km**params["gamma"]
    )
    estimate *= 1_000_000_000
    return int(max(DEFAULT_TRAFFIC_FLOOR, min(DEFAULT_TRAFFIC_CEILING, estimate)))


def calibrate_gravity_model(routes_df: pd.DataFrame, throughput_df: pd.DataFrame) -> dict[str, float]:
    """
    Fit a log-linear gravity model against observed traffic and return coefficients and R².
    """
    if routes_df.empty:
        return {"K": 0.0005, "alpha": 0.7, "beta": 0.7, "gamma": 1.2, "r2": 0.0}

    lookup = throughput_df.set_index("iata")["total_pax_millions"].to_dict()
    frame = routes_df.copy()
    frame["throughput_a"] = frame["origin_iata"].map(lookup)
    frame["throughput_b"] = frame["dest_iata"].map(lookup)
    frame["annual_pax"] = pd.to_numeric(frame["annual_pax"], errors="coerce")
    frame["distance_nm"] = pd.to_numeric(frame["distance_nm"], errors="coerce")
    frame = frame.dropna(subset=["throughput_a", "throughput_b", "annual_pax", "distance_nm"])
    if len(frame) < 5:
        return {"K": 0.0005, "alpha": 0.7, "beta": 0.7, "gamma": 1.2, "r2": 0.0}

    features = np.column_stack(
        [
            np.ones(len(frame)),
            np.log(frame["throughput_a"].to_numpy()),
            np.log(frame["throughput_b"].to_numpy()),
            np.log(frame["distance_nm"].clip(lower=250).to_numpy() * 1.852),
        ]
    )
    target = np.log(frame["annual_pax"].clip(lower=1).to_numpy())
    coeffs, _, _, _ = np.linalg.lstsq(features, target, rcond=None)
    fitted = features @ coeffs
    residual = ((target - fitted) ** 2).sum()
    total = ((target - target.mean()) ** 2).sum()
    r2 = 1 - residual / total if total else 0.0
    return {
        "K": float(np.exp(coeffs[0]) / 1_000_000_000),
        "alpha": float(coeffs[1]),
        "beta": float(coeffs[2]),
        "gamma": float(-coeffs[3]),
        "r2": float(max(0.0, min(1.0, r2))),
    }
