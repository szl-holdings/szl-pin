"""Every assertion executed green before this file was pushed."""
from szl_pin import pin_diff, pin_estate

H = lambda c: c * 40
V1 = [("szl-crosscheck", H("a")), ("szl-eclipse", H("b")), ("szl-ci-witness", H("c"))]
V2 = [("szl-crosscheck", H("a")), ("szl-eclipse", H("9")), ("szl-ci-witness", H("c")),
      ("szl-vertical-forge", H("d"))]


def test_pin_is_deterministic_and_order_independent():
    p1 = pin_estate(V1)
    assert p1["state"] == "MEASURED" and p1["pinned_repos"] == 3
    assert pin_estate(V1)["estate_hash"] == p1["estate_hash"]
    assert pin_estate(list(reversed(V1)))["estate_hash"] == p1["estate_hash"]


def test_drift_names_every_moved_and_added_head():
    d = pin_diff(pin_estate(V1), pin_estate(V2))
    assert d["moved"] == ["szl-eclipse"]
    assert d["moved_detail"]["szl-eclipse"] == {"from": "bbbbbbbb", "to": "99999999"}
    assert d["added"] == ["szl-vertical-forge"]
    assert d["removed"] == []
    assert d["same"] is False


def test_identical_pins_report_same():
    assert pin_diff(pin_estate(V1), pin_estate(V1))["same"] is True


def test_bad_sha_fails_closed():
    assert pin_estate([("repo", "notasha")])["state"] == "INVALID"
    assert pin_estate([("repo", "ab12")])["state"] == "INVALID"


def test_empty_estate_and_non_measured_inputs():
    assert pin_estate([])["state"] == "MEASURED"
    assert pin_estate([])["pinned_repos"] == 0
    assert pin_diff(pin_estate(V1), {"state": "INVALID"})["state"] == "INVALID"
