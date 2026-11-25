# szl-pin domain leader study r1 (propose-only)

Date: 2026-11-25. Method: web-verified leader landscape + owner-direct execution (standing authority GREENLIGHT-RULING-2026-11-24-K1 rank5; the Kimi ratification seat remains stood down by explicit owner directive, disclosed; owner-direct nonce T22-OWNER-DIRECT-20261125-K1). Study pinned to szl-pin HEAD 6db82be96751ab920132642f5da740438dca2a1d, fetched 2026-11-25. This card is documentation only; it changes no code, CI, config, or existing PR status. All absorb actions are FUTURE PROPOSALS (non-authorizing); implementation and merges remain separately reviewed and gated. L Conjecture 1: OPEN (advisory, never a closed theorem). No speedup, energy, or proven-trust claims; upstream performance claims are labeled as upstream claims only. No unverified signing, attestation, or provenance-level claims; this study verifies nothing about this repo's artifacts.

## Domain: Estate pinning: one SHA-256 hash commits to every repo head in the frontier; deterministic, order-independent, offline-verifiable; pin_diff names every moved/added/removed head; fail-closed SHA validation.

## Leaders studied (web-verified 2026-11-25)
1. Git (https://github.com/git/git) - moat: the object model whose content-addressing underlies any head-pinning scheme.
2. The Update Framework (https://github.com/theupdateframework/python-tuf) - moat: the reference implementation of target metadata and rotation discipline.
3. OpenSSL (https://github.com/openssl/openssl) - moat: the digest standard implementation ground truth for SHA-256 behavior.

## Absorb actions (FUTURE PROPOSALS, non-authorizing)
1. (Git) Propose a documentation-only review of head-identity documentation conventions (a pin names exact 40-char heads, never branch names alone). Cost: doc-only; limit: note only.
2. (python-tuf) Propose a documentation-only note on rotation vocabulary for pin-set updates (moved/added/removed named per update). Cost: doc-only; limit: note only.
3. (OpenSSL) Propose a documentation-only review of digest determinism documentation (order-independence stated with its verification recipe). Cost: doc-only; limit: note only.
4. Baseline preserve honestly: drift is never silent (pin_diff discipline documented as-is); offline verifiability claimed only with its recipe; fail-closed validation semantics preserved; no trust claims about pinned content beyond identity.

## Do not do (per governing seat)

Do not merge, bypass the signature wall, or claim implementation beyond this card.
