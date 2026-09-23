# szl-pin

One hash commits to a supplied frontier snapshot. `pin_estate` takes unique
repository names and full head SHAs and produces a single `estate_hash` — same
pairs, same hash, any machine, order-independent and offline-verifiable.
`pin_diff` validates both pins before naming every moved, added, or removed
repository head.

A pin proves the exact caller-supplied set. It does **not** prove that the input
census was complete, fresh, authorized, healthy, deployed, or live. Bind those
claims through the applicable source census, CI witness, publication receipt,
runtime readback, and proof/evaluation records.

## Why

The estate ships fast, with repository heads moving throughout a work session.
A source-qualified census can be converted into one recomputable snapshot hash,
and a later qualified snapshot can be compared with a diff that names the
changed repositories. Compose those records with CI witnesses and provider or
runtime receipts without treating any one layer as proof of another.

## Usage

```bash
pip install -e . pytest && python -m pytest tests/ -q
python -m szl_pin.pin pin --heads heads.json --by stephen --note "friday pin"
python -m szl_pin.pin diff --a pin-1400.json --b pin-1600.json
```

`heads.json` is `[ ["szl-crosscheck", "51193553..."], ...]` using full 40-character
commit SHAs. Repository names must be non-empty, trimmed, and unique
(case-insensitively) within the input.

## Fail-closed verification

Before comparing pins, `pin_diff` revalidates each input's schema, entry shape,
unique repository names, SHA format, declared repository count, and recomputed
canonical SHA-256. Malformed, ambiguous, or tampered pins return `INVALID`
rather than being collapsed into an apparently clean diff.

## Historical evidence boundary

`receipts/2026-09-05T00:51Z-alignment-sweep-1.json` is preserved as a historical,
explicitly partial census artifact. It is not a `szl.estate-pin/v1` head pin and
must not be passed to `pin_diff` or represented as a complete current estate
snapshot.

## Doctrine

- A head is a 40-character hexadecimal commit SHA or pinning fails closed.
- Repository names are non-empty, trimmed, and unique within a pin.
- Entries are sorted by repository name; caller order never changes the hash.
- Each input pin is self-verified before a drift result is emitted.
- A pin is a snapshot of supplied facts, not a claim of census completeness,
  health, publication, or runtime state.

## License

Apache-2.0 — canonical organization text (see LICENSE pointer).
