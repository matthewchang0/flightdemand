from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import pandas as pd

from pipeline.config import BTI_PATH, CITY_ALIASES


def normalize_city_name(city: str) -> str:
    normalized = (city or "").strip().lower().replace(".", "")
    return CITY_ALIASES.get(normalized, normalized)


@lru_cache(maxsize=1)
def load_bti(filepath: Path | str = BTI_PATH) -> pd.DataFrame:
    return pd.read_csv(filepath)


def get_bti(city: str, throughput_rank: float | None = None, filepath: Path | str = BTI_PATH) -> float:
    """
    Look up or estimate a business travel index score for a city.
    """
    normalized = normalize_city_name(city)
    bti = load_bti(filepath)
    match = bti.loc[bti["city_norm"] == normalized]
    if not match.empty:
        return float(match.iloc[0]["total"])
    if throughput_rank is None:
        return 35.0
    return float(max(25.0, min(70.0, 20.0 + (1.0 - throughput_rank) * 50.0)))

