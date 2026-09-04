# szl-pin

One hash commits to the whole frontier. `pin_estate` takes every repo's head
SHA and produces a single `estate_hash` — same heads, same hash, any machine,
order-independent, offline-verifiable. `pin_diff` takes two pins and names
every moved, added, or removed head. Drift is never silent.

## Why

The estate ships fast — ten frontier repos in one session, heads moving hourly.
"What exactly was live at 14:00?" is now one recomputable hash, and "what
changed since" is one diff that names names. Compose it with the consolidation
receipts (which pin Spaces) and ci-witness (which pins runs): the estate gets
a complete, verifiable timeline.

## Usage

```bash
pip install -e . pytest && python -m pytest tests/ -q
python -m szl_pin.pin pin --heads heads.json --by stephen --note "friday pin"
python -m szl_pin.pin diff --a pin-1400.json --b pin-1600.json
```

`heads.json` is `[ ["szl-crosscheck", "51193553..."], ...]` — full 40-char SHAs.

## Verified behavior (pre-push, 2026-09-04)

Deterministic and order-independent pins; a drift report naming
`szl-eclipse bbbbbbbb → 99999999` plus an added repo; identical pins report
`same: true`; malformed SHAs and non-MEASURED inputs fail closed; an empty
estate pins honestly with `pinned_repos: 0`. Suite: 5/5 green.

## Doctrine

- A head is a 40-char hex SHA or the pin fails closed.
- Entries are sorted by repo — position never changes the hash.
- A pin is a snapshot of fact, not a claim of health. Health is the benches' job.

## License

Apache-2.0 — canonical org text (see LICENSE pointer).
