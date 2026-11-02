"""Ambiguous JSON must not be collapsed into a clean estate diff."""
import json

import pytest

from szl_pin import pin_estate
from szl_pin.pin import main


@pytest.mark.parametrize("side", ["a", "b"])
@pytest.mark.parametrize("field", [
    "head", "equal_head", "escaped_head", "repo", "entries",
    "pinned_repos", "estate_hash",
])
def test_cli_rejects_duplicate_keys_before_validating_pin(tmp_path, capsys, side, field):
    pin = pin_estate([("repo", "a" * 40)])
    valid = json.dumps(pin)
    replacements = {
        "head": ('"head":', '"head": "' + "b" * 40 + '", "head":'),
        "equal_head": ('"head":', '"head": "' + "a" * 40 + '", "head":'),
        "escaped_head": ('"head":', '"he\\u0061d": "' + "b" * 40 + '", "head":'),
        "repo": ('"repo":', '"repo": "other", "repo":'),
        "entries": ('"entries":', '"entries": [], "entries":'),
        "pinned_repos": ('"pinned_repos":', '"pinned_repos": 999, "pinned_repos":'),
        "estate_hash": ('"estate_hash":', '"estate_hash": "' + "0" * 64 + '", "estate_hash":'),
    }
    old, new = replacements[field]
    ambiguous = valid.replace(old, new, 1)
    paths = {name: tmp_path / f"{name}.json" for name in ("a", "b")}
    for name, path in paths.items():
        path.write_text(ambiguous if name == side else valid, encoding="utf-8")

    assert main(["diff", "--a", str(paths["a"]), "--b", str(paths["b"])]) == 2
    output = capsys.readouterr()
    assert output.out == ""
    assert "duplicate JSON key" in output.err
    assert paths[side].read_text(encoding="utf-8") == ambiguous


@pytest.mark.parametrize("head,same", [("a" * 40, True), ("b" * 40, False)])
def test_cli_accepts_unambiguous_pins_and_preserves_diff(tmp_path, capsys, head, same):
    a, b = tmp_path / "a.json", tmp_path / "b.json"
    a.write_text(json.dumps(pin_estate([("repo", "a" * 40)])), encoding="utf-8")
    b.write_text(json.dumps(pin_estate([("repo", head)])), encoding="utf-8")
    assert main(["diff", "--a", str(a), "--b", str(b)]) == 0
    output = capsys.readouterr()
    result = json.loads(output.out)
    assert output.err == ""
    assert result["state"] == "MEASURED"
    assert result["same"] is same
    assert result["moved"] == ([] if same else ["repo"])
