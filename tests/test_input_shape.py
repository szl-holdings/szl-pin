"""Malformed census containers must not become measured empty estate pins."""
import json

import pytest

from szl_pin import pin_estate
from szl_pin.pin import main


@pytest.mark.parametrize("value", [{}, "", b"", bytearray(), {("repo", "a" * 40): "ignored"}])
def test_pin_rejects_non_pair_containers(value):
    result = pin_estate(value)
    assert result["state"] == "INVALID"
    assert "estate_hash" not in result


@pytest.mark.parametrize("value", [{}, ""])
def test_cli_rejects_wrong_json_container(tmp_path, capsys, value):
    heads = tmp_path / "heads.json"
    heads.write_text(json.dumps(value), encoding="utf-8")
    assert main(["pin", "--heads", str(heads)]) == 2
    result = json.loads(capsys.readouterr().out)
    assert result["state"] == "INVALID"
    assert "estate_hash" not in result


def test_cli_still_accepts_explicit_empty_list(tmp_path, capsys):
    heads = tmp_path / "heads.json"
    heads.write_text("[]", encoding="utf-8")
    assert main(["pin", "--heads", str(heads)]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["state"] == "MEASURED"
    assert result["pinned_repos"] == 0


def test_pair_generators_remain_supported():
    pairs = ((name, "a" * 40) for name in ("one", "two"))
    result = pin_estate(pairs)
    assert result["state"] == "MEASURED"
    assert result["pinned_repos"] == 2
