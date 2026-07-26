# OpenAPI v1 sketch (TASK-API-001)

- `POST /api/v1/calculate/qimen` — single system cast + interpret
- `POST /api/v1/calculate/all` — multi-system (premium+)
- `POST /api/v1/timing/optimize` — STRAT-001 (501 until mounted)
- `POST /api/v1/scenario/compare` — STRAT-002 (501 until mounted)
- `GET /api/v1/reports/{id}` — 404 until API-004
- `GET /api/v1/knowledge/patterns` — seeded pattern catalog (TASK-API-005)
  - Query: `system` (canonical: `qimen`|`liuren`|`taiyi`), `he` (alias, incl. `ky_mon`|`luc_nham`|`thai_at`), `q` (search), `limit` (1..500, default 200)
  - Unknown `system`/`he` → HTTP 200 with `patterns: []`, `total: 0`
  - Response: `{ patterns: [...], total: number, source: "tamthuc_kb.seed" }`
- Errors: `{ error: { code, message, request_id, details? } }`
