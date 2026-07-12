# API versioning policy (FR-API-002)

## Scheme

- **Primary:** URL prefix `/api/v{major}/…` (e.g. `/api/v1/calculate/qimen`).
- **Option:** request header `X-API-Version: {major}`.
- **Precedence:** when both URL and header are present, **the URL wins**.

Unsupported majors are rejected with the FR-API-001 error envelope (`NOT_FOUND`), never silently rewritten to another version.

## Breaking vs additive

| Change | Classification | Action |
|---|---|---|
| Remove / rename field, change type or meaning, tighten validation | **Breaking** | New major version + `CHANGELOG.md` entry with migration guidance |
| New optional field, new endpoint | **Additive** | Same major; note in changelog optional |

## Deprecation window

- A deprecated field or endpoint **continues to function** for **at least 2–3 major versions** after deprecation.
- Responses carry:
  - `Deprecation: true`
  - `Link: <successor>; rel="successor-version"`
  - `Sunset: <HTTP-date>` when a date is set
- Exact window per item is recorded in `CHANGELOG.md` and the `Sunset` header.

## Stability invariant (strategy 4.3)

| Surface | Stability | Changes via |
|---|---|---|
| Calculation output (la so envelope / chart `ban`) | **Stable**, reproducible | FR-PLAT-002 `envelope_version` bump + migration note only |
| Interpretation (RAG-003 prose) | **May vary** / improve | Not version-frozen; not byte-stable |
| Request/response field set | Additive within a major; breaking → new major | This policy + `CHANGELOG.md` |

Clients may pin chart/envelope equality across API majors for the same input; they **must not** pin interpretation prose.
