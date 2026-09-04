"""szl-pin: estate pinning and drift.

One SHA-256 hash commits to every repo head in the frontier. Same heads, same
hash, any machine - order-independent, offline-verifiable. pin_diff names
every moved, added, or removed head between two pins. Drift is never silent.

Doctrine:
- A head is a 40-char hex SHA or the pin fails closed.
- The pin commits to repo+head pairs sorted by name - nothing positional.
- A pin is a snapshot of fact, not a claim of health. Health is the benches' job.
"""
from __future__ import annotations
import argparse, hashlib, json, sys
from typing import Any, Dict, Iterable, List, Tuple

_HEX = set("0123456789abcdef")

def pin_estate(repos: Iterable[Tuple[str, str]], captured_by: str = "operator", note: str = "") -> Dict[str, Any]:
    """repos: iterable of (repo, head_sha40). One hash commits to the entire frontier state."""
    entries: List[Dict[str, str]] = []
    for repo, sha in repos:
        if not isinstance(sha, str) or len(sha) != 40 or not set(sha.lower()) <= _HEX:
            return {"state": "INVALID", "detail": f"{repo}: head must be a 40-char hex SHA"}
        entries.append({"repo": repo, "head": sha.lower()})
    entries.sort(key=lambda e: e["repo"])
    canon = json.dumps({"entries": entries}, sort_keys=True, separators=(",", ":"))
    return {"state": "MEASURED", "schema": "szl.estate-pin/v1",
            "pinned_repos": len(entries), "entries": entries,
            "estate_hash": hashlib.sha256(canon.encode()).hexdigest(),
            "captured_by": captured_by, "note": note,
            "label": "estate pin - one hash commits to every repo head; recompute, never trust"}

def pin_diff(pin_a: Dict[str, Any], pin_b: Dict[str, Any]) -> Dict[str, Any]:
    """Drift report between two pins. Every moved head named; nothing silent."""
    for p in (pin_a, pin_b):
        if p.get("state") != "MEASURED":
            return {"state": "INVALID", "detail": "both inputs must be MEASURED pins"}
    a = {e["repo"]: e["head"] for e in pin_a["entries"]}
    b = {e["repo"]: e["head"] for e in pin_b["entries"]}
    moved = sorted(r for r in set(a) & set(b) if a[r] != b[r])
    added = sorted(set(b) - set(a))
    removed = sorted(set(a) - set(b))
    return {"state": "MEASURED", "moved": moved, "added": added, "removed": removed,
            "moved_detail": {r: {"from": a[r][:8], "to": b[r][:8]} for r in moved},
            "same": pin_a["estate_hash"] == pin_b["estate_hash"] and not (moved or added or removed),
            "label": "estate drift - every moved head named, none silent"}

def _load_pin(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="szl-pin")
    p.add_argument("command", choices=["pin", "diff"])
    p.add_argument("--heads", help="path to a JSON list of [repo, head_sha] pairs")
    p.add_argument("--a", help="pin A file (for diff)")
    p.add_argument("--b", help="pin B file (for diff)")
    p.add_argument("--by", default="operator")
    p.add_argument("--note", default="")
    args = p.parse_args(argv)
    if args.command == "pin":
        if not args.heads:
            print("pin needs --heads", file=sys.stderr)
            return 2
        with open(args.heads, "r", encoding="utf-8") as f:
            pairs = json.load(f)
        print(json.dumps(pin_estate([tuple(x) for x in pairs], captured_by=args.by, note=args.note), indent=2))
        return 0
    if not (args.a and args.b):
        print("diff needs --a and --b", file=sys.stderr)
        return 2
    print(json.dumps(pin_diff(_load_pin(args.a), _load_pin(args.b)), indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
