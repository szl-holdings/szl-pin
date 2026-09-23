"""Contract tests for deterministic, self-verifying estate pins."""
from copy import deepcopy

from szl_pin import pin_diff, pin_estate

H = lambda c: c * 40
V1 = [
    ("szl-crosscheck", H("a")),
    ("szl-eclipse", H("b")),
    ("szl-ci-witness", H("c")),
]
V2 = [
    ("szl-crosscheck", H("a")),
    ("szl-eclipse", H("9")),
    ("szl-ci-witness", H("c")),
    ("szl-vertical-forge", H("d")),
]


def test_pin_is_deterministic_and_order_independent():
    p1 = pin_estate(V1)
    assert p1["state"] == "MEASURED" and p1["pinned_repos"] == 3
    assert pin_estate(V1)["estate_hash"] == p1["estate_hash"]
    assert pin_estate(list(reversed(V1)))["estate_hash"] == p1["estate_hash"]


def test_drift_names_every_moved_and_added_head():
    drift = pin_diff(pin_estate(V1), pin_estate(V2))
    assert drift["moved"] == ["szl-eclipse"]
    assert drift["moved_detail"]["szl-eclipse"] == {
        "from": "bbbbbbbb",
        "to": "99999999",
    }
    assert drift["added"] == ["szl-vertical-forge"]
    assert drift["removed"] == []
    assert drift["same"] is False


def test_identical_pins_report_same():
    assert pin_diff(pin_estate(V1), pin_estate(V1))["same"] is True


def test_bad_sha_and_bad_repo_fail_closed():
    assert pin_estate([("repo", "notasha")])["state"] == "INVALID"
    assert pin_estate([("repo", "ab12")])["state"] == "INVALID"
    assert pin_estate([("", H("a"))])["state"] == "INVALID"
    assert pin_estate([(" repo", H("a"))])["state"] == "INVALID"
    assert pin_estate([(None, H("a"))])["state"] == "INVALID"


def test_duplicate_repository_names_fail_closed():
    assert pin_estate([("repo", H("a")), ("repo", H("b"))])["state"] == "INVALID"
    assert pin_estate([("Repo", H("a")), ("repo", H("b"))])["state"] == "INVALID"


def test_empty_estate_and_non_measured_inputs():
    assert pin_estate([])["state"] == "MEASURED"
    assert pin_estate([])["pinned_repos"] == 0
    assert pin_diff(pin_estate(V1), {"state": "INVALID"})["state"] == "INVALID"


def test_diff_rejects_tampered_hash_and_count():
    pin = pin_estate(V1)
    bad_hash = deepcopy(pin)
    bad_hash["estate_hash"] = "0" * 64
    assert pin_diff(pin, bad_hash) == {
        "state": "INVALID",
        "detail": "pin B: estate_hash does not match canonical entries",
    }

    bad_count = deepcopy(pin)
    bad_count["pinned_repos"] = 999
    assert pin_diff(bad_count, pin) == {
        "state": "INVALID",
        "detail": "pin A: pinned_repos does not match entries",
    }


def test_diff_rejects_duplicate_or_malformed_entries_without_raising():
    pin = pin_estate(V1)
    duplicate = deepcopy(pin)
    duplicate["entries"].append(dict(duplicate["entries"][0]))
    duplicate["pinned_repos"] += 1
    assert pin_diff(duplicate, pin)["state"] == "INVALID"

    malformed = deepcopy(pin)
    malformed["entries"] = [{"repo": "repo"}]
    malformed["pinned_repos"] = 1
    assert pin_diff(malformed, pin)["state"] == "INVALID"


def test_diff_rejects_schema_drift_and_unexpected_entry_fields():
    pin = pin_estate(V1)
    wrong_schema = deepcopy(pin)
    wrong_schema["schema"] = "szl.estate-pin/v2"
    assert pin_diff(wrong_schema, pin)["state"] == "INVALID"

    extra_field = deepcopy(pin)
    extra_field["entries"][0]["claim"] = "healthy"
    assert pin_diff(extra_field, pin)["state"] == "INVALID"
