#!/usr/bin/env python3
"""
Build the Business Travel Index (BTI) lookup table.

This script writes a curated, explainable city-level lookup for large-airport markets.
The scores are synthesized from public rankings and tiering guidance rather than direct
licensed datasets, which keeps the portfolio project reproducible.
"""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "data" / "processed" / "business_travel_index.csv"

ROWS = [
    ("New York", 30, 25, 20, 14, 9),
    ("London", 29, 24, 20, 14, 9),
    ("Tokyo", 28, 24, 18, 13, 8),
    ("Hong Kong", 22, 17, 19, 12, 8),
    ("Singapore", 21, 17, 19, 14, 9),
    ("San Francisco", 23, 18, 16, 10, 10),
    ("Paris", 25, 20, 18, 14, 7),
    ("Shanghai", 24, 20, 16, 10, 8),
    ("Dubai", 18, 17, 19, 12, 7),
    ("Chicago", 23, 20, 16, 10, 7),
    ("Los Angeles", 23, 18, 14, 11, 8),
    ("Beijing", 24, 20, 16, 10, 7),
    ("Sydney", 18, 14, 17, 11, 8),
    ("Frankfurt", 18, 18, 18, 9, 6),
    ("Seoul", 19, 17, 15, 10, 8),
    ("Toronto", 18, 15, 15, 11, 7),
    ("Zurich", 16, 14, 18, 9, 6),
    ("Boston", 18, 14, 14, 8, 9),
    ("Washington DC", 18, 16, 15, 11, 6),
    ("Seattle", 17, 14, 13, 8, 9),
    ("Mumbai", 18, 16, 12, 9, 7),
    ("Sao Paulo", 18, 15, 13, 9, 6),
    ("Amsterdam", 17, 14, 16, 10, 6),
    ("Dublin", 14, 12, 13, 10, 8),
    ("Tel Aviv", 15, 13, 13, 8, 8),
    ("Dallas", 18, 16, 12, 8, 7),
    ("Houston", 17, 15, 11, 7, 6),
    ("Miami", 16, 13, 12, 10, 6),
    ("Bangkok", 16, 12, 10, 11, 6),
    ("Taipei", 15, 12, 13, 8, 7),
    ("Melbourne", 15, 12, 14, 9, 7),
    ("Geneva", 14, 11, 16, 9, 5),
    ("Munich", 16, 13, 15, 8, 6),
    ("Madrid", 16, 13, 13, 10, 6),
    ("Milan", 16, 13, 14, 9, 6),
    ("Doha", 13, 12, 16, 8, 5),
    ("Abu Dhabi", 13, 11, 15, 8, 5),
    ("Osaka", 15, 12, 12, 8, 6),
    ("Jakarta", 16, 12, 10, 7, 6),
    ("Kuala Lumpur", 15, 11, 11, 8, 6),
    ("Atlanta", 18, 14, 11, 8, 6),
    ("Denver", 15, 12, 10, 7, 6),
    ("Philadelphia", 15, 12, 11, 7, 5),
    ("Johannesburg", 14, 11, 11, 8, 6),
    ("Istanbul", 16, 13, 12, 9, 6),
    ("Delhi", 17, 15, 10, 8, 7),
    ("Mexico City", 17, 14, 10, 9, 6),
    ("Bangalore", 16, 12, 9, 7, 9),
    ("Stockholm", 14, 11, 14, 8, 6),
    ("Copenhagen", 14, 11, 14, 8, 6),
    ("Vienna", 14, 11, 14, 8, 5),
    ("Brussels", 14, 11, 14, 9, 5),
    ("Montreal", 14, 11, 12, 8, 6),
    ("Vancouver", 14, 11, 12, 8, 7),
    ("Lisbon", 13, 10, 11, 9, 5),
    ("Barcelona", 14, 11, 11, 9, 6),
    ("Warsaw", 13, 10, 10, 8, 6),
    ("Prague", 12, 10, 10, 8, 6),
    ("Helsinki", 12, 9, 11, 7, 6),
    ("Oslo", 12, 9, 11, 7, 6),
    ("Edinburgh", 11, 9, 10, 8, 5),
    ("Riyadh", 13, 11, 11, 7, 5),
    ("Auckland", 12, 9, 11, 7, 6),
    ("Brisbane", 11, 9, 10, 7, 6),
    ("Perth", 11, 8, 10, 6, 5),
    ("San Jose", 15, 10, 10, 6, 9),
    ("San Diego", 13, 10, 9, 6, 8),
    ("Austin", 13, 10, 9, 6, 8),
    ("Phoenix", 13, 10, 8, 6, 7),
    ("Minneapolis", 13, 10, 8, 6, 6),
    ("Detroit", 13, 10, 9, 6, 6),
    ("Charlotte", 12, 10, 8, 6, 6),
    ("Orlando", 11, 8, 7, 8, 5),
    ("Las Vegas", 11, 8, 7, 9, 5),
    ("Nashville", 10, 8, 7, 6, 6),
    ("Portland", 11, 8, 8, 6, 7),
    ("Salt Lake City", 11, 8, 8, 6, 6),
    ("Santiago", 13, 10, 9, 7, 6),
    ("Bogota", 12, 10, 8, 7, 6),
    ("Lima", 12, 9, 8, 7, 5),
    ("Buenos Aires", 13, 10, 9, 7, 5),
    ("Panama City", 12, 9, 8, 7, 5),
    ("Rio de Janeiro", 12, 9, 8, 8, 5),
    ("Cape Town", 11, 8, 8, 8, 5),
    ("Nairobi", 11, 8, 8, 7, 5),
    ("Casablanca", 11, 8, 8, 7, 5),
    ("Cairo", 12, 9, 8, 7, 5),
    ("Athens", 12, 9, 9, 7, 5),
    ("Budapest", 11, 8, 9, 7, 5),
    ("Bucharest", 10, 8, 8, 7, 5),
    ("Dusseldorf", 12, 9, 10, 7, 5),
    ("Hamburg", 11, 9, 9, 7, 5),
    ("Manchester", 12, 9, 9, 8, 5),
    ("Birmingham", 10, 8, 8, 7, 5),
    ("Glasgow", 10, 8, 8, 7, 5),
    ("Lyon", 10, 8, 8, 7, 5),
    ("Marseille", 9, 7, 7, 7, 5),
    ("Nice", 10, 8, 8, 8, 5),
    ("Rome", 14, 11, 12, 10, 5),
    ("Naples", 9, 7, 7, 7, 4),
    ("Venice", 9, 7, 7, 8, 4),
    ("Turin", 9, 7, 7, 7, 5),
    ("Chennai", 12, 9, 8, 6, 7),
    ("Hyderabad", 12, 9, 8, 6, 8),
    ("Pune", 10, 8, 7, 5, 7),
    ("Shenzhen", 16, 12, 10, 6, 8),
    ("Guangzhou", 16, 12, 10, 6, 7),
    ("Chengdu", 14, 11, 9, 6, 6),
    ("Hangzhou", 14, 11, 9, 6, 7),
    ("Manila", 13, 10, 8, 7, 6),
    ("Ho Chi Minh City", 13, 10, 8, 7, 6),
    ("Hanoi", 11, 9, 7, 7, 6),
]


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            [
                "city",
                "city_norm",
                "gdp_score",
                "hq_score",
                "finance_score",
                "events_score",
                "tech_score",
                "total",
            ]
        )
        for city, gdp, hq, finance, events, tech in ROWS:
            total = gdp + hq + finance + events + tech
            writer.writerow([city, city.lower(), gdp, hq, finance, events, tech, total])
    print(f"Wrote {len(ROWS)} BTI rows to {OUTPUT}")


if __name__ == "__main__":
    main()
