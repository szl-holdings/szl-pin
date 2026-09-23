"""szl-pin: estate pinning and drift.

One SHA-256 hash commits to every supplied repo head. Same heads, same hash,
any machine - order-independent, offline-verifiable. ``pin_diff`` validates
both pins before naming every moved, added, or removed head.

Doctrine:
- A head is a 40-char hex SHA or the pin fails closed.
- Repository names are non-empty strings and unique within a pin.
- The pin commits to repo+head pairs sorted by name - nothing positional.
- A pin is a snapshot of supplied facts, not proof of census completeness or health.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections.abc import Iterable, Mapping, Sequence
from typing import Any, Dict, List, Tuple

_HEX = frozenset("0123456789abcdef")
_SCHEMA = "szl.estate-pin/v1"


def _invalid(detail: str) -> Dict[str, Any]:
    return {"state": "INVALID", "detail": detail}


def _valid_repo_name(repo: object) -> bool:
    return isinstance(repo, str) and bool(repo) and repo == repo.strip()


def _valid_sha(sha: object, length: int) -> bool:
    return (
        isinstance(sha, str)
        and len(sha) == length
        and bool(sha)
        and set(sha.lower()) <= _HEX
    )


def _canonical_entries(
    repos: Iterable[Tuple[str, str]],
) -> tuple[List[Dict[str, str]] | None, str | None]:
    entries: List[Dict[str, str]] = []
    seen: set[str] = set()
    try:
        iterator = iter(repos)
    except TypeError:
        return None, "repos must be an iterable of (repo, head) pairs"

    for index, item in enumerate(iterator):
        if (
            not isinstance(item, Sequence)
            or isinstance(item, (str, bytes))
            or len(item) != 2
        ):
            return None, f"entry {index}: expected [repo, head]"
        repo, sha = item
        if not _valid_repo_name(repo):
            return None, f"entry {index}: repo must be a non-empty trimmed string"
        repo_key = repo.casefold()
        if repo_key in seen:
            return None, f"{repo}: duplicate repository name"
        seen.add(repo_key)
        if not _valid_sha(sha, 40):
            return None, f"{repo}: head must be a 40-char hex SHA"
        entries.append({"repo": repo, "head": sha.lower()})

    entries.sort(key=lambda entry: entry["repo"])
    return entries, None


def _estate_hash(entries: List[Dict[str, str]]) -> str:
    canonical = json.dumps(
        {"entries": entries}, sort_keys=True, separators=(",", ":")
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _validated_pin(
    pin: object,
) -> tuple[List[Dict[str, str]] | None, str | None]:
    if not isinstance(pin, Mapping):
        return None, "pin must be an object"
    if pin.get("state") != "MEASURED":
        return None, "pin state must be MEASURED"
    if pin.get("schema") != _SCHEMA:
        return None, f"pin schema must be {_SCHEMA}"

    raw_entries = pin.get("entries")
    if not isinstance(raw_entries, list):
        return None, "pin entries must be a list"

    pairs: List[Tuple[str, str]] = []
    for index, entry in enumerate(raw_entries):
        if not isinstance(entry, Mapping):
            return None, f"entry {index}: must be an object"
        if set(entry) != {"repo", "head"}:
            return None, f"entry {index}: expected exactly repo and head"
        pairs.append((entry.get("repo"), entry.get("head")))  # type: ignore[arg-type]

    entries, error = _canonical_entries(pairs)
    if error:
        return None, error
    assert entries is not None

    if pin.get("pinned_repos") != len(entries):
        return None, "pinned_repos does not match entries"

    claimed_hash = pin.get("estate_hash")
    if not _valid_sha(claimed_hash, 64):
        return None, "estate_hash must be a 64-char hex SHA-256"
    expected_hash = _estate_hash(entries)
    if claimed_hash.lower() != expected_hash:
        return None, "estate_hash does not match canonical entries"

    return entries, None


def pin_estate(
    repos: Iterable[Tuple[str, str]],
    captured_by: str = "operator",
    note: str = "",
) -> Dict[str, Any]:
    """Commit to a caller-supplied iterable of unique ``(repo, head_sha40)`` pairs."""
    entries, error = _canonical_entries(repos)
    if error:
        return _invalid(error)
    assert entries is not None
    return {
        "state": "MEASURED",
        "schema": _SCHEMA,
        "pinned_repos": len(entries),
        "entries": entries,
        "estate_hash": _estate_hash(entries),
        "captured_by": captured_by,
        "note": note,
        "label": (
            "estate pin - hash commits to supplied repo heads; "
            "verify completeness separately"
        ),
    }


def pin_diff(pin_a: Dict[str, Any], pin_b: Dict[str, Any]) -> Dict[str, Any]:
    """Validate two pins before reporting every moved, added, or removed head."""
    entries_a, error_a = _validated_pin(pin_a)
    if error_a:
        return _invalid(f"pin A: {error_a}")
    entries_b, error_b = _validated_pin(pin_b)
    if error_b:
        return _invalid(f"pin B: {error_b}")
    assert entries_a is not None and entries_b is not None

    a = {entry["repo"]: entry["head"] for entry in entries_a}
    b = {entry["repo"]: entry["head"] for entry in entries_b}
    moved = sorted(repo for repo in set(a) & set(b) if a[repo] != b[repo])
    added = sorted(set(b) - set(a))
    removed = sorted(set(a) - set(b))
    return {
        "state": "MEASURED",
        "moved": moved,
        "added": added,
        "removed": removed,
        "moved_detail": {
            repo: {"from": a[repo][:8], "to": b[repo][:8]} for repo in moved
        },
        "same": not (moved or added or removed),
        "label": "estate drift - validated pins, every changed repo head named",
    }


def _load_pin(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError("pin file must contain a JSON object")
    return value


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="szl-pin")
    parser.add_argument("command", choices=["pin", "diff"])
    parser.add_argument("--heads", help="path to a JSON list of [repo, head_sha] pairs")
    parser.add_argument("--a", help="pin A file (for diff)")
    parser.add_argument("--b", help="pin B file (for diff)")
    parser.add_argument("--by", default="operator")
    parser.add_argument("--note", default="")
    args = parser.parse_args(argv)

    try:
        if args.command == "pin":
            if not args.heads:
                print("pin needs --heads", file=sys.stderr)
                return 2
            with open(args.heads, "r", encoding="utf-8") as handle:
                pairs = json.load(handle)
            result = pin_estate(pairs, captured_by=args.by, note=args.note)
        else:
            if not (args.a and args.b):
                print("diff needs --a and --b", file=sys.stderr)
                return 2
            result = pin_diff(_load_pin(args.a), _load_pin(args.b))
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"szl-pin: {exc}", file=sys.stderr)
        return 2

    print(json.dumps(result, indent=2))
    return 0 if result.get("state") == "MEASURED" else 2


if __name__ == "__main__":
    raise SystemExit(main())
