from pipeline.ingest.aircraft_perf import SubsonicAircraft, SupersonicAircraft
from pipeline.transform.time_savings import compute_time_savings


def test_jfk_lhr():
    result = compute_time_savings(2991, 0.97, SupersonicAircraft(), SubsonicAircraft())
    assert 2.7 <= result["time_saved_hr"] <= 4.3


def test_jfk_lax_time_savings():
    result = compute_time_savings(2470, 0.0, SupersonicAircraft(), SubsonicAircraft())
    assert 1.0 <= result["time_saved_hr"] <= 2.5


def test_sfo_nrt():
    result = compute_time_savings(4427, 0.98, SupersonicAircraft(), SubsonicAircraft())
    assert 3.0 <= result["time_saved_hr"] <= 4.9


def test_lhr_dxb():
    result = compute_time_savings(2998, 0.45, SupersonicAircraft(), SubsonicAircraft())
    assert 1.1 <= result["time_saved_hr"] <= 2.8


def test_sfo_jfk_boomless_reference():
    result = compute_time_savings(2246, 0.12, SupersonicAircraft(), SubsonicAircraft())
    assert 3.2 <= result["supersonic_block_hr"] <= 3.8


def test_dca_lax_boomless_reference():
    result = compute_time_savings(2005, 0.03, SupersonicAircraft(), SubsonicAircraft())
    assert 3.3 <= result["supersonic_block_hr"] <= 4.1
