from pipeline.transform.route_builder import build_candidate_routes


def test_distance_filter():
    airports = __sample_airports()
    routes = build_candidate_routes(airports)
    assert (routes["distance_nm"] >= 1500).all()
    assert (routes["distance_nm"] <= 5500).all()


def test_deduplication():
    airports = __sample_airports()
    routes = build_candidate_routes(airports)
    assert len(routes.loc[(routes["origin_iata"] == "JFK") & (routes["dest_iata"] == "LHR")]) == 1
    assert len(routes.loc[(routes["origin_iata"] == "LHR") & (routes["dest_iata"] == "JFK")]) == 0


def test_large_airports_only():
    airports = __sample_airports()
    routes = build_candidate_routes(airports)
    assert set(routes["origin_iata"]).issubset({"JFK", "LHR", "LAX", "NRT"})


def __sample_airports():
    import pandas as pd

    return pd.DataFrame(
        [
            {"iata": "JFK", "city": "New York", "country": "United States", "country_code": "US", "lat": 40.64, "lon": -73.78, "type": "large_airport"},
            {"iata": "LHR", "city": "London", "country": "United Kingdom", "country_code": "GB", "lat": 51.47, "lon": -0.45, "type": "large_airport"},
            {"iata": "LAX", "city": "Los Angeles", "country": "United States", "country_code": "US", "lat": 33.94, "lon": -118.40, "type": "large_airport"},
            {"iata": "NRT", "city": "Tokyo", "country": "Japan", "country_code": "JP", "lat": 35.77, "lon": 140.39, "type": "large_airport"},
        ]
    )

