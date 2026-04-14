from __future__ import annotations

from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
OUTPUT_DATA_DIR = DATA_DIR / "output"
DASHBOARD_DIR = ROOT_DIR / "dashboard"
DASHBOARD_PUBLIC_DIR = DASHBOARD_DIR / "public"

AIRPORTS_PATH = RAW_DATA_DIR / "airports.csv"
LAND_GEOJSON_PATH = RAW_DATA_DIR / "ne_110m_land.geojson"
T100_PATH = RAW_DATA_DIR / "t100_international.csv"
T100_SAMPLE_PATH = RAW_DATA_DIR / "t100_sample.csv"
EUROSTAT_PATH = RAW_DATA_DIR / "eurostat_avia_par.tsv"
THROUGHPUT_PATH = RAW_DATA_DIR / "airport_throughput.csv"
BTI_PATH = PROCESSED_DATA_DIR / "business_travel_index.csv"

ROUTES_JSON_PATH = OUTPUT_DATA_DIR / "routes.json"
ROUTES_CSV_PATH = OUTPUT_DATA_DIR / "routes.csv"
SUMMARY_JSON_PATH = OUTPUT_DATA_DIR / "summary.json"
DASHBOARD_ROUTES_PATH = DASHBOARD_PUBLIC_DIR / "routes.json"
DASHBOARD_SUMMARY_PATH = DASHBOARD_PUBLIC_DIR / "summary.json"

MIN_ROUTE_DISTANCE_NM = 1500.0
MAX_ROUTE_DISTANCE_NM = 5000.0
SOFT_MAX_ROUTE_DISTANCE_NM = 5500.0
OVERTURE_RANGE_LIMIT_NM = 4250.0
OVERWATER_SAMPLE_INTERVAL_NM = 20.0
TAXI_OVERHEAD_HR = 0.5
TOP_CANDIDATE_LIMIT = 2500

PREMIUM_PAX_SHARE = 0.15
SUPERSONIC_CAPTURE_RATE = 0.30
DEFAULT_LOAD_FACTOR = 0.80
DEFAULT_CONNECTIVITY_FACTOR = 0.02
DEFAULT_TRAFFIC_FLOOR = 50_000
DEFAULT_TRAFFIC_CEILING = 2_000_000

FARE_YIELD_BANDS = {
    "transatlantic": (0.35, 0.55),
    "transpacific": (0.25, 0.40),
    "intra_europe": (0.50, 0.80),
    "middle_east_long_haul": (0.30, 0.45),
    "intra_asia": (0.30, 0.50),
    "americas_long_haul": (0.28, 0.42),
    "default_long_haul": (0.30, 0.45),
}

COUNTRY_NAME_MAP = {
    "AE": "United Arab Emirates",
    "AU": "Australia",
    "BE": "Belgium",
    "BR": "Brazil",
    "CA": "Canada",
    "CH": "Switzerland",
    "CN": "China",
    "DE": "Germany",
    "DK": "Denmark",
    "ES": "Spain",
    "FI": "Finland",
    "FR": "France",
    "GB": "United Kingdom",
    "HK": "Hong Kong",
    "IE": "Ireland",
    "IL": "Israel",
    "IN": "India",
    "IT": "Italy",
    "JP": "Japan",
    "KR": "South Korea",
    "MX": "Mexico",
    "NL": "Netherlands",
    "NO": "Norway",
    "PT": "Portugal",
    "QA": "Qatar",
    "SA": "Saudi Arabia",
    "SE": "Sweden",
    "SG": "Singapore",
    "TR": "Turkey",
    "TW": "Taiwan",
    "US": "United States",
    "ZA": "South Africa",
}

AIRPORT_CITY_OVERRIDES = {
    "BWI": "Washington DC",
    "DCA": "Washington DC",
    "EWR": "New York",
    "FLL": "Miami",
    "HND": "Tokyo",
    "IAD": "Washington DC",
    "JFK": "New York",
    "LGA": "New York",
    "NRT": "Tokyo",
    "OAK": "San Francisco",
    "SJC": "San Jose",
}

CITY_ALIASES = {
    "abu dhabi": "abu dhabi",
    "amsterdam schiphol": "amsterdam",
    "beijing": "beijing",
    "boston": "boston",
    "charlotte": "charlotte",
    "chicago": "chicago",
    "dallas": "dallas",
    "dallas-fort worth": "dallas",
    "dubai": "dubai",
    "frankfurt": "frankfurt",
    "hong kong": "hong kong",
    "istanbul": "istanbul",
    "london": "london",
    "los angeles": "los angeles",
    "miami": "miami",
    "munich": "munich",
    "new york": "new york",
    "newark": "new york",
    "osaka": "osaka",
    "paris": "paris",
    "rome": "rome",
    "san francisco": "san francisco",
    "seattle": "seattle",
    "seoul": "seoul",
    "singapore": "singapore",
    "sydney": "sydney",
    "tokyo": "tokyo",
    "toronto": "toronto",
    "washington": "washington dc",
    "washington dc": "washington dc",
    "zurich": "zurich",
}

REGION_GROUPS = {
    "north_america": {"US", "CA", "MX"},
    "europe": {
        "AT",
        "BE",
        "CH",
        "CZ",
        "DE",
        "DK",
        "ES",
        "FI",
        "FR",
        "GB",
        "GR",
        "HU",
        "IE",
        "IT",
        "NL",
        "NO",
        "PL",
        "PT",
        "RO",
        "SE",
        "TR",
    },
    "middle_east": {"AE", "IL", "QA", "SA"},
    "asia": {"CN", "HK", "ID", "IN", "JP", "KR", "MY", "PH", "SG", "TH", "TW", "VN"},
    "oceania": {"AU", "NZ"},
    "latin_america": {"AR", "BR", "CL", "CO", "PE"},
    "africa": {"EG", "KE", "MA", "NG", "ZA"},
}


def ensure_directories() -> None:
    for path in (RAW_DATA_DIR, PROCESSED_DATA_DIR, OUTPUT_DATA_DIR, DASHBOARD_PUBLIC_DIR):
        path.mkdir(parents=True, exist_ok=True)

