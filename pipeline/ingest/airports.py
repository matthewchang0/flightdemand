from __future__ import annotations

from pathlib import Path

import pandas as pd

from pipeline.config import AIRPORTS_PATH, AIRPORT_CITY_OVERRIDES, COUNTRY_NAME_MAP


def _resolve_city(row: pd.Series) -> str:
    iata = row.get("iata_code")
    municipality = str(row.get("municipality") or "").strip()
    if iata in AIRPORT_CITY_OVERRIDES:
        return AIRPORT_CITY_OVERRIDES[iata]
    return municipality


def load_airports(min_type: str = "large_airport", filepath: Path | str = AIRPORTS_PATH) -> pd.DataFrame:
    """
    Load OurAirports data and normalize fields used throughout the pipeline.
    """
    airports = pd.read_csv(filepath, dtype={"iata_code": "string", "icao_code": "string"})
    filtered = airports.loc[airports["type"] == min_type].copy()
    filtered = filtered.dropna(subset=["iata_code", "latitude_deg", "longitude_deg"])
    filtered["iata"] = filtered["iata_code"].str.upper()
    filtered["icao"] = filtered["icao_code"].fillna("").str.upper()
    filtered["city"] = filtered.apply(_resolve_city, axis=1)
    filtered["country"] = filtered["iso_country"].map(COUNTRY_NAME_MAP).fillna(filtered["iso_country"])
    filtered["country_code"] = filtered["iso_country"].fillna("")
    filtered["lat"] = filtered["latitude_deg"].astype(float)
    filtered["lon"] = filtered["longitude_deg"].astype(float)
    filtered["elevation_ft"] = filtered["elevation_ft"].fillna(0).astype(float)
    columns = [
        "iata",
        "icao",
        "name",
        "city",
        "country",
        "country_code",
        "lat",
        "lon",
        "elevation_ft",
        "type",
    ]
    return filtered.loc[:, columns].drop_duplicates(subset=["iata"]).reset_index(drop=True)

