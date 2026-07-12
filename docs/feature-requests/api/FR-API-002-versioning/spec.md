---
id: FR-API-002
title: "API versioning and deprecation policy - URL versioning (/api/v1, /api/v2) as primary with a header-versioning option, deprecated fields kept >= 2-3 versions behind a Deprecation warning header, a CHANGELOG of breaking changes, and the invariant that calculation output stays stable while interpretation may vary"
module: API
priority: SHOULD
status: done
phase: P1
slice: 1
lang: python
effort_h: 6
owner: Stephen Cheng (Founder/CPO)
created: 2026-07-08
refs: [Grok-49, strategy 4.1, strategy 4.3]
related_frs: [FR-API-001, FR-PLAT-002, FR-PLAT-004, FR-WEB-006]
depends_on: [FR-API-001]
blocks: []
new_paths:
  - packages/tamthuc_api/tamthuc_api/versioning/__init__.py
  - packages/tamthuc_api/tamthuc_api/versioning/router.py
  - packages/tamthuc_api/tamthuc_api/versioning/deprecation.py
  - packages/tamthuc_api/tests/test_versioning.py
  - docs/contracts/api-versioning-policy.md
  - CHANGELOG.md
---

## §1 - Description (BCP-14 normative)

This FR defines how the API evolves without breaking the clients that depend on it: URL versioning as the primary scheme, a header-versioning option, a deprecation policy with a support window, a changelog of breaking changes, and the invariant that separates what may change (interpretation) from what may not (calculation output). It extends the `tamthuc_api` package and wraps the FR-API-001 routes. It owns the versioning scheme and the deprecation mechanics; it does NOT change the endpoint behavior FR-API-001 defines - it governs how that behavior may change over time.

The API SHALL version by URL as the primary scheme (`/api/v1`, `/api/v2`), and MAY additionally accept a version header as an option for clients that prefer it; when both are present the URL SHALL win. A breaking change - removing or renaming a field, changing a type, changing the meaning of a value, tightening validation - SHALL require a new major version; an additive change (a new optional field, a new endpoint) SHALL NOT. A deprecated field or endpoint SHALL be retained for at least 2-3 versions after deprecation, SHALL continue to function during that window, and SHALL be served with a `Deprecation` (and where useful `Sunset`) warning header naming the replacement, so a client is told in-band that it is on a path that will end. Every breaking change SHALL be documented in a `CHANGELOG.md` with the version, the change, and the migration guidance.

One invariant SHALL hold across all versioning: the calculation output MUST stay stable while the interpretation MAY vary. The la so envelope (FR-PLAT-002) and the deterministic chart it carries are a versioned contract that changes only through PLAT-002's own version bump with a migration note; the AI interpretation (RAG-003) is expected to improve and reword across versions and is NOT held to byte-stability. The versioning layer SHALL make this explicit so a client can rely on the chart being reproducible while accepting that the interpretation prose evolves.

## §2 - Why this design (rationale for humans)

An API with real clients (the web app, a future mobile app, Enterprise API-key integrations) cannot change shape underneath them without breaking them, but it also cannot freeze forever. Versioning is the contract that lets the API evolve on a schedule the clients can follow. URL versioning is chosen as primary because it is the most visible and cache-friendly scheme - the version is right there in the path, a proxy or a log shows it, and there is no ambiguity about which contract a request expects (Grok-49). The header option exists for clients that prefer content negotiation, but the URL wins when both are present so there is always one unambiguous answer. Making breaking-versus-additive an explicit rule keeps the team from shipping a silent breaking change as a point release - a renamed field is a new major version, full stop.

The deprecation window with an in-band warning header is the difference between an evolution and an outage. Keeping a deprecated field working for 2-3 versions and telling the client, in the response itself, that it is deprecated and what replaces it, gives integrators time to migrate on their own schedule rather than discovering a break in production. The changelog is the human-readable companion to that machine signal. The calculation-stable / interpretation-variable invariant is the versioning expression of the platform's spine (strategy 4.3): the whole product rests on the chart being deterministic and reproducible, so the calculation output is the last thing that may drift casually - it changes only through the FR-PLAT-002 versioned envelope. The interpretation, by contrast, is supposed to get better, so holding it to byte-stability would freeze the very thing the RAG work is meant to improve. Separating the two tells clients exactly what they can pin against and what they cannot.

## §3 - Contract (scheme / deprecation / changelog)

### Versioning scheme (`versioning/router.py`, `docs/contracts/api-versioning-policy.md`)

- Primary: URL - `/api/v1/...`, `/api/v2/...`. Every FR-API-001 route is mounted under a version prefix.
- Option: a version header (e.g. `X-API-Version: 1` or an `Accept` media-type parameter); the URL wins when both are present.
- Breaking change -> new major version. Additive change -> same version. The policy file enumerates what counts as each.

### Deprecation (`versioning/deprecation.py`)

```python
# a deprecated field/endpoint keeps working for >= 2-3 versions and carries warning headers
def deprecation_headers(replacement: str, sunset: str | None) -> dict:
    # Deprecation: true ; Link: <replacement>; rel="successor-version" ; Sunset: <date?>
    ...
```

| Response header | Meaning |
|---|---|
| `Deprecation: true` | this field/endpoint is deprecated |
| `Link: <...>; rel="successor-version"` | where to migrate |
| `Sunset: <http-date>` | when support ends (>= 2-3 versions out) |

### The stability invariant (`docs/contracts/api-versioning-policy.md`)

| Surface | Stability | Changes via |
|---|---|---|
| calculation output (la so envelope, chart) | stable, reproducible | FR-PLAT-002 `envelope_version` bump + migration note only |
| interpretation (RAG-003 prose) | may vary / improve | not version-frozen; not byte-stable |
| request/response field set | additive within a version; breaking -> new major | this policy + `CHANGELOG.md` |

### Changelog (`CHANGELOG.md`)

Every breaking change recorded with the version, the change, and migration guidance; additive changes noted; the deprecation window stated per deprecated item.

## §4 - Acceptance criteria

1. All FR-API-001 routes are served under a URL version prefix (`/api/v1/...`); a request to an unknown version returns the FR-API-001 error envelope with the correct status, not a silent fallback.
2. The header-versioning option is honored when present, and the URL version wins when both a URL and a header version are supplied (a conflict test asserts the precedence).
3. A deprecated field/endpoint continues to function and is served with `Deprecation` (and, where set, `Sunset`) headers naming the successor; a test asserts the field still works and the headers are present.
4. A deprecated item is retained for at least 2-3 versions after deprecation before removal; the policy and `CHANGELOG.md` record the deprecation and the planned sunset.
5. The calculation output is stable across API versions - the la so envelope changes only via a FR-PLAT-002 `envelope_version` bump, never as an unversioned API change - while the interpretation is allowed to vary; a test pins the chart and does not pin the interpretation prose.
6. Every breaking change is documented in `CHANGELOG.md` with migration guidance; a CI check fails a breaking change that lacks a changelog entry and a version bump.

## §5 - Verification

- `tests/test_versioning.py`: URL routing per version; header option honored; URL-wins-on-conflict; deprecated field still functions and carries the warning headers; unknown-version rejection in the error envelope.
- A stability test: the calculation output (envelope) is byte-stable across two API versions for a golden input, while the interpretation field is explicitly not asserted byte-stable; a change to the envelope shape without a FR-PLAT-002 version bump fails.
- A changelog/contract check in CI: a route or field change flagged as breaking must have a `CHANGELOG.md` entry and a version increment, or the check fails.
- Gates: `ruff check`, `ruff format --check`, `mypy tamthuc_api`, `pytest packages/tamthuc_api`; the OpenAPI (FR-API-001 `openapi-v1.md`) is emitted per version.

## §6 - Implementation skeleton

1. `versioning/router.py`: mount the FR-API-001 routes under `/api/v{n}`; resolve the effective version (URL primary, header option, URL wins); reject unknown versions in the error envelope.
2. `versioning/deprecation.py`: the `Deprecation`/`Link`/`Sunset` header helper and a decorator to mark a field/endpoint deprecated with its successor and sunset.
3. `docs/contracts/api-versioning-policy.md`: the breaking-vs-additive rules, the 2-3 version support window, and the calculation-stable / interpretation-variable invariant.
4. `CHANGELOG.md`: seed with v1; establish the entry format; wire the CI check that a breaking change carries an entry + a version bump.
5. Confirm the calculation-stability invariant against FR-PLAT-002 (the envelope changes only via its own version bump).

## §7 - Dependencies

Depends on FR-API-001 (the routes, the error envelope, and the OpenAPI contract this FR versions and wraps; unknown-version rejection uses the API-001 envelope). Enforces the calculation-stability half of the invariant against the FR-PLAT-002 la so envelope contract (the chart changes only via `envelope_version`, never as an unversioned API change), while leaving the FR-RAG-003 interpretation free to vary. Coordinates with FR-PLAT-004 (the CI check for changelog + version bump on a breaking change runs in the pipeline) and FR-WEB-006 (the frontend/i18n consumers pin to a version). Blocks nothing directly; it is a governance layer over the existing gateway.

## §8 - Example payloads

```
# URL versioning (primary); a deprecated field still works but is flagged
GET /api/v1/knowledge/patterns?system=qimen
HTTP/1.1 200 OK
Deprecation: true
Link: </api/v2/knowledge/patterns>; rel="successor-version"
Sunset: Wed, 08 Jul 2026 00:00:00 GMT
```

```json
// CHANGELOG.md entry (abridged) - a breaking change with migration guidance
{ "version": "v2", "breaking": [
  { "change": "renamed response field 'cach_cuc' array item 'score' -> 'weight'",
    "migrate": "read 'weight'; 'score' remains in v1 until sunset" } ] }
```

## §9 - Open questions

- Header scheme specifics: a custom `X-API-Version` vs an `Accept` media-type parameter (`application/vnd.tamthuc.v2+json`). Default: a simple `X-API-Version` header as the option, with the URL as primary and authoritative; the media-type scheme is a later addition if a client needs strict content negotiation.
- Support-window length: 2 vs 3 versions. Default: retain a deprecated item for 3 versions where cheap and at least 2 always; the exact window per item is stated in the changelog and the `Sunset` header, not left implicit.
- Whether Enterprise API-key clients get a longer deprecation window than the web app. Default: one policy for all clients at MVP; a negotiated longer window for Enterprise integrations is a later contractual option that reuses the same `Sunset` mechanism.

## §10 - Failure modes inventory

| Mode | Trigger | Required behavior |
|---|---|---|
| Silent breaking change | a field renamed/removed within a version | forbidden; a breaking change requires a new major version + a CHANGELOG entry; CI fails otherwise |
| Abrupt removal | a deprecated item removed with no window | retained >= 2-3 versions with `Deprecation`/`Sunset` headers naming the successor |
| Ambiguous version | URL and header disagree | the URL wins; a conflict test asserts the precedence |
| Unknown version guessed | a request to an unsupported version silently served | rejected in the FR-API-001 error envelope, not a silent fallback |
| Calculation drift | the chart/envelope changes as an unversioned API change | forbidden; the calculation output changes only via a FR-PLAT-002 `envelope_version` bump |
| Frozen interpretation | interpretation held to byte-stability | not required; interpretation may vary/improve across versions and is not version-frozen |

## §11 - Notes

This FR is governance, not new behavior: it lets the API-001 gateway evolve without breaking its clients. Hold the scheme (URL primary, header optional, URL wins), the window (a deprecated item lives >= 2-3 versions behind `Deprecation`/`Sunset` headers and a CHANGELOG entry), and above all the invariant that separates the two halves of the platform - calculation output is stable and reproducible, changing only through the FR-PLAT-002 versioned envelope, while interpretation is free to improve. That split is the versioning face of the deterministic-engine / AI-layer boundary (strategy 4.3): clients pin to the chart, not to the prose. It extends the same `tamthuc_api` app as FR-API-001/003/004, so the gateway stays one installable, mypy-clean unit.
