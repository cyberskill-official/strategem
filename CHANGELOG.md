# Changelog

All notable API and contract changes are documented here (FR-API-002).

Format: each major records **breaking** (with migration) and **additive** notes. Deprecated items state the deprecation major, successor, and planned sunset (retained ≥ 2–3 majors).

## [v1] — 2026-07-08

### Added

- Initial public API under `/api/v1` (FR-API-001): calculate (qimen / liuren / taiyi / all), knowledge patterns, reports, timing.
- URL-primary versioning with optional `X-API-Version` header; URL wins on conflict (FR-API-002).
- Calculation-stable / interpretation-variable invariant documented in `docs/contracts/api-versioning-policy.md`.

### Deprecated

- `/api/v1/knowledge/patterns` marked for successor `/api/v2/knowledge/patterns` when v2 lands.
  - `deprecated_in`: v1
  - `remove_in`: v4 (retained 3 majors after deprecation)
  - `Sunset`: Wed, 08 Jul 2027 00:00:00 GMT
  - Endpoint remains fully functional in v1; responses may carry `Deprecation` / `Link` / `Sunset`.

### Stability

- Chart / la so calculation output changes only via FR-PLAT-002 `envelope_version`.
- Interpretation prose is not held to byte-stability across releases.
