# Changelog

## 0.1.2 (unreleased)

### Fixed

- Align runtime `__version__` with distribution metadata; add an installed-package version regression.
- Require a nonnegative integer repository count and reject malformed census containers (#13, #19).
- Reject duplicate JSON object keys before loading pins for comparison (#20).

### Packaging

- Sync the canonical release gate, including isolated installed-wheel probes and dependency checks, and add its wheel-isolation regressions.

The implementation fixes above are changes since 0.1.1 already present on main. This release preparation changes version identity, packaging validation, and tests. Earlier releases are documented in the repository's GitHub Releases.
