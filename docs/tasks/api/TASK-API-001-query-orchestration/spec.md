---
id: TASK-API-001
title: "Query orchestration - the FastAPI gateway, the nine-step query flow (auth -> CORE calendar -> engine cast -> RULE detect -> RAG interpret -> report -> return -> persist), endpoint contracts, and the structured error envelope; never re-computes a chart"
module: API
priority: MUST
status: done
phase: P0
slice: 1
lang: python
effort_h: 14
owner: Stephen Cheng (Founder/CPO)
created: 2026-07-08
refs: [strategy 4.2, Grok-06, Grok-12]
related_frs: [TASK-AUTH-001, TASK-AUTH-002, TASK-CORE-005, TASK-QMDG-006, TASK-RULE-003, TASK-RAG-003, TASK-REPORT-001, TASK-API-003, TASK-API-004, TASK-PLAT-002]
depends_on: [TASK-AUTH-001, TASK-CORE-005]
blocks: [TASK-API-002, TASK-API-003, TASK-API-004, TASK-WEB-002]
new_paths:
  - packages/tamthuc_api/pyproject.toml
  - packages/tamthuc_api/tamthuc_api/__init__.py
  - packages/tamthuc_api/tamthuc_api/app.py
  - packages/tamthuc_api/tamthuc_api/schemas.py
  - packages/tamthuc_api/tamthuc_api/errors.py
  - packages/tamthuc_api/tamthuc_api/orchestrator.py
  - packages/tamthuc_api/tamthuc_api/clients/__init__.py
  - packages/tamthuc_api/tamthuc_api/clients/core.py
  - packages/tamthuc_api/tamthuc_api/clients/engine.py
  - packages/tamthuc_api/tamthuc_api/clients/rule.py
  - packages/tamthuc_api/tamthuc_api/clients/rag.py
  - packages/tamthuc_api/tamthuc_api/routes/calculate.py
  - packages/tamthuc_api/tamthuc_api/routes/knowledge.py
  - packages/tamthuc_api/tamthuc_api/routes/reports.py
  - packages/tamthuc_api/tamthuc_api/routes/timing.py
  - packages/tamthuc_api/tests/test_orchestration.py
  - packages/tamthuc_api/tests/test_error_envelope.py
  - docs/contracts/api-error-envelope.schema.json
  - docs/contracts/openapi-v1.md
---

## §1 - Description (BCP-14 normative)

This task builds the API gateway and the query orchestration that binds the whole platform: the FastAPI application, the endpoint contracts, the nine-step query flow (strategy 4.2), and the structured error envelope every endpoint returns on failure. It is the birth of the `tamthuc_api` package. It owns the orchestration and the request/response and error contracts; it does NOT implement rate limiting (TASK-API-003) nor persistence and audit (TASK-API-004), though it defines the seams both plug into.

The gateway SHALL expose these v1 endpoints: `POST /api/v1/calculate/{qimen,liuren,taiyi,all}`, `POST /api/v1/timing/optimize`, `POST /api/v1/scenario/compare`, `GET /api/v1/knowledge/patterns?system=`, `POST /api/v1/reports/generate`, and `GET /api/v1/reports/{id}/download`, and SHALL mount the TASK-AUTH-001 auth routes (`POST /auth/{register,login,refresh}`). Authentication SHALL be JWT Bearer for user principals and an API key for Enterprise principals (both resolved by TASK-AUTH-001/002). The strategic endpoints (`/timing/optimize`, `/scenario/compare`) SHALL expose their contract here and delegate to TASK-STRAT-001/002 when present, returning a typed not-implemented error until those land.

The orchestrator SHALL implement the nine steps in order: (1) accept the validated query; (2) authenticate and authorize, then resolve the calendar context via CORE; (3) call the selected engine(s) to cast the chart from that context; (4) call RULE to detect patterns; (5) call RAG to retrieve grounded knowledge; (6) build the prompt and call the LLM through RAG; (7) assemble the structured report; (8) return chart plus patterns plus cited interpretation plus AIDisclosure to the caller; (9) persist the query, chart, patterns, report, and flags with an audit row (steps 5-8 via RAG/REPORT, step 9 via TASK-API-004). The gateway SHALL treat the la so JSON envelope (TASK-PLAT-002) as read-only: it passes the engine's chart to RULE and RAG and NEVER re-computes or mutates `ban`, `cach_cuc`, `lich_phap`, or `co_truong_phai`. Every failure SHALL return the structured error envelope `{ code, message, details }` with the correct standard HTTP status.

## §2 - Why this design (rationale for humans)

The nine-step flow is the product's spinal cord - it is where the deterministic branch and the interpretation branch are actually joined, in order, per request (strategy 4.2). Writing it as one explicit orchestrator rather than letting each route improvise means the contract "engine casts, AI interprets, nobody re-computes" is enforced in one readable place, and the read-only invariant on the la so envelope is checkable. If the gateway could re-derive a chart field, determinism and reproducibility would be gone the moment the AI layer disagreed with the engine; making the gateway a pass-through for the envelope is what keeps the boundary real (strategy 4.3, RISK-8).

A single structured error envelope is a small decision with large downstream value. The frontend, the SDK, and every operator dashboard parse one shape - `code` for branching, `message` for humans, `details` for context - instead of guessing at ad hoc error bodies. Standard HTTP codes carry the coarse signal (401 vs 403 vs 429 vs 502) and the `code` carries the fine one. Exposing the strategic endpoints' contracts now, even as typed not-implemented, lets the frontend and the OpenAPI consumers build against the final shape while STRAT is still P1 - the URL and the request body do not change when the implementation lands.

## §3 - Contract (API / schemas / flow)

### Request and response (`tamthuc_api/schemas.py`)

```python
class QueryRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    datetime: str                 # ISO local time of the question / event
    tz: str                       # e.g. "+07:00"
    place: str | None             # human place; resolved to kinh_do
    kinh_do: float | None         # longitude override
    question_type: str            # loai_cau_hoi (trach_thoi, hon_nhan, ...)
    systems: list[str]            # ["qimen"] | ["qimen","liuren"] | ["all"]
    persona_level: str = "beginner"   # controls RAG framing
    co_truong_phai: dict | None   # optional school-flag overrides; else defaults

class QueryResponse(BaseModel):
    query_id: str
    charts: list[LaSo]            # the TASK-PLAT-002 envelope(s), read-only
    patterns: list[CachCuc]
    interpretation: Interpretation    # cited, structured, from RAG-003
    ai_disclosure: AIDisclosure       # mandatory on any AI output
```

### Error envelope (`tamthuc_api/errors.py`, contract `docs/contracts/api-error-envelope.schema.json`)

```json
{ "error": { "code": "STRING_ENUM", "message": "human-readable",
             "details": { "...": "context" }, "request_id": "..." } }
```

| HTTP | code (examples) | When |
|---:|---|---|
| 400 | `VALIDATION_ERROR` | malformed body / bad datetime |
| 401 | `UNAUTHENTICATED` | missing/invalid token |
| 403 | `FORBIDDEN_TIER` | tier lacks the capability (TASK-AUTH-002) |
| 404 | `NOT_FOUND` | unknown report id |
| 422 | `UNPROCESSABLE` | valid shape, un-castable input |
| 429 | `RATE_LIMITED` | quota exceeded (TASK-API-003) |
| 500 | `INTERNAL` | unexpected |
| 501 | `NOT_IMPLEMENTED` | strategic endpoint pending STRAT |
| 502 / 503 | `UPSTREAM_ENGINE` / `UPSTREAM_LLM` | engine or LLM failure (TASK-PLAT-008 degradation) |

### Orchestrator (`tamthuc_api/orchestrator.py`) - the nine steps

```python
async def run_query(req: QueryRequest, principal: Principal) -> QueryResponse:
    # 1. req is already validated by the QueryRequest model
    # 2. authorize (capability for the requested systems) + resolve calendar context via CORE (clients/core)
    ctx = await core.resolve_calendar(req.datetime, req.tz, req.kinh_do, req.co_truong_phai)
    # 3. cast the chart(s) with the selected engine(s); returns the la so envelope, READ-ONLY here
    charts = [await engine.cast(sys, ctx, req) for sys in resolve_systems(req.systems)]
    # 4. detect patterns via RULE (clients/rule.match)
    patterns = await rule.match(charts)
    # 5-6. RAG retrieves grounded knowledge and calls the LLM (clients/rag.interpret)
    interp = await rag.interpret(charts, patterns, req.question_type, req.persona_level)
    # 7. assemble the structured report (REPORT-001; inline summary at P0 if REPORT not present)
    # 8. build QueryResponse (chart + patterns + cited interpretation + AIDisclosure)
    # 9. persist + audit  (delegated to TASK-API-004; the orchestrator calls the persistence seam)
    return response
```

Steps 3 and 4 pass the la so envelope by reference to RULE and RAG; the orchestrator asserts the returned envelope is byte-identical to the cast one (the read-only invariant). `clients/*` are thin adapters over the Rust engine service, the RULE match API, and the RAG package.

### Endpoints (`tamthuc_api/routes/*`)

`calculate.py` maps `/calculate/{system}` to `run_query`; `/calculate/all` fans out to every engine and returns the multi-chart response. `knowledge.py` serves `GET /knowledge/patterns?system=` from TASK-RULE-003 / the seeded set. `reports.py` serves `POST /reports/generate` and `GET /reports/{id}/download` (TASK-REPORT-001/002). `timing.py` exposes `/timing/optimize` and `/scenario/compare` contracts, delegating to STRAT or returning `NOT_IMPLEMENTED`.

## §4 - Acceptance criteria

1. `POST /api/v1/calculate/qimen` with a valid body runs the nine steps and returns `{ query_id, charts, patterns, interpretation, ai_disclosure }`; the response chart is byte-identical to the engine's cast envelope (no gateway re-computation).
2. The orchestrator calls CORE, then the engine, then RULE, then RAG, in that order; a test with stubbed clients asserts the call sequence and that RULE and RAG receive the same envelope the engine produced.
3. Every error path returns the envelope `{ error: { code, message, details, request_id } }` with the correct HTTP status per the table; a validation failure is 400 `VALIDATION_ERROR`, an unknown report id is 404 `NOT_FOUND`, an engine failure is 502 `UPSTREAM_ENGINE`.
4. `/calculate/all` returns one chart per system and a single fused response; `/calculate/qimen` for a Free principal is allowed, `/calculate/all` for a Free principal is 403 `FORBIDDEN_TIER` (TASK-AUTH-002 capability).
5. `/timing/optimize` and `/scenario/compare` return their typed contract and, without STRAT present, a 501 `NOT_IMPLEMENTED`; the request/response shapes match `docs/contracts/openapi-v1.md`.
6. The AIDisclosure block is present on every response carrying interpretation and is never stripped by the gateway; a response without it fails a contract test.

## §5 - Verification

- `tests/test_orchestration.py`: the nine-step call-order test with stubbed CORE/engine/RULE/RAG clients; the read-only-envelope byte-equality assertion; `/calculate/all` fan-out; the tier-capability gate; AIDisclosure presence.
- `tests/test_error_envelope.py`: each HTTP-code/`code` pair from the table; the envelope validates against `docs/contracts/api-error-envelope.schema.json`; `request_id` is present and echoed from the request context.
- Contract: the emitted OpenAPI matches `docs/contracts/openapi-v1.md` for paths, methods, and the error schema; a drift check fails CI.
- Gates: `ruff check`, `ruff format --check`, `mypy tamthuc_api`, `pytest packages/tamthuc_api`.

## §6 - Implementation skeleton

1. Create the `tamthuc_api` package (`pyproject.toml`, `uv`-managed per TASK-PLAT-001); this task owns its birth, TASK-API-002/003/004 add modules.
2. `app.py`: the FastAPI app, router mount, the TASK-AUTH-001 auth dependency, the exception handlers that render the error envelope, and the `request_id` middleware.
3. `schemas.py` + `errors.py`: `QueryRequest` / `QueryResponse`, the error envelope, the code enum; author `docs/contracts/api-error-envelope.schema.json`.
4. `clients/*`: thin adapters over CORE, the engine service, RULE match, and RAG interpret (stubbable for tests).
5. `orchestrator.py`: `run_query` implementing the nine steps with the read-only-envelope assertion.
6. `routes/*`: calculate, knowledge, reports, timing; wire the persistence/audit seam for TASK-API-004; author `docs/contracts/openapi-v1.md`.

## §7 - Dependencies

Depends on TASK-AUTH-001 (the auth dependency and mounted auth routes) and TASK-CORE-005 (the calendar context resolved in step 2). Calls TASK-QMDG-006 (and later TASK-LN-006 / TASK-TAT-006) to cast, TASK-RULE-003 to detect, TASK-RAG-003 to interpret, and TASK-REPORT-001 to assemble; reads the TASK-PLAT-002 la so envelope read-only. Blocks TASK-API-002 (versioning wraps these routes), TASK-API-003 (rate limiting middleware on these routes), TASK-API-004 (persistence/audit on step 9), and TASK-WEB-002 (the query input screen calls `/calculate/*`). Capability gating uses TASK-AUTH-002; upstream failure handling coordinates with TASK-PLAT-008 resilience.

## §8 - Example payloads

```json
// POST /api/v1/calculate/qimen
{ "datetime": "2004-01-01T10:30:00", "tz": "+07:00", "place": "Ha Noi", "kinh_do": 105.85,
  "question_type": "trach_thoi", "systems": ["qimen"], "persona_level": "beginner" }
```

```json
// 200 response (abridged)
{ "query_id": "q_...", "charts": [ { "he": "ky_mon", "dau_vao": {...}, "lich_phap": {...},
    "ban": {...}, "cach_cuc": [ { "id": "qimen_thanh_long_hoi_dau", "polarity": "cat" } ],
    "co_truong_phai": {...} } ],
  "patterns": [ ... ], "interpretation": { "beginner": "...", "citations": [ ... ] },
  "ai_disclosure": { "ai_generated": true, "review_status": "auto", "model": "..." } }
```

```json
// 429 error envelope
{ "error": { "code": "RATE_LIMITED", "message": "Daily request quota exceeded for the Free tier.",
             "details": { "limit": 100, "reset_at": "..." }, "request_id": "req_..." } }
```

## §9 - Open questions

- Rust engine transport: an HTTP service call vs a PyO3/WASM in-process binding. Default: an HTTP service client at MVP behind `clients/engine.py` so the boundary is a network contract the read-only assertion can guard; an in-process binding is a later optimization that keeps the same client interface (strategy 4.1, DEC-2).
- Sync vs async report generation for `/reports/generate`. Default: synchronous inline assembly at P0 (REPORT-001 is P1; the orchestrator returns an inline summary until then); an async job with `GET /reports/{id}` polling is the P1 shape. Coordinate with TASK-REPORT-001.
- Whether `/calculate/all` interpretation is one fused reading or per-system readings plus an agreement view. Default: per-system charts now, with cross-system agreement deferred to TASK-STRAT-004; the response shape already carries a list of charts so adding the agreement view is additive.

## §10 - Failure modes inventory

| Mode | Trigger | Required behavior |
|---|---|---|
| Gateway re-computes a chart | orchestrator mutates or re-derives `ban`/`cach_cuc`/`lich_phap` | forbidden; byte-equality assertion on the returned envelope fails the test; no engine logic in the gateway |
| Out-of-order flow | RAG called before RULE, or engine skipped | the orchestrator fixes the nine-step order; the call-order test fails on any deviation |
| Ad hoc error body | a route returns a non-envelope error | central exception handlers render the envelope for every raised error; a test asserts no bare error bodies |
| Missing AIDisclosure | interpretation returned without the disclosure block | contract test rejects; the response model requires `ai_disclosure` when `interpretation` is present |
| Upstream failure leaks 500 | engine/LLM error surfaced as opaque 500 | mapped to 502/503 `UPSTREAM_*` with degradation per TASK-PLAT-008, not a generic 500 |
| Tier bypass | a capability-gated endpoint reached without the tier | TASK-AUTH-002 dependency on every gated route; 403 `FORBIDDEN_TIER` |

## §11 - Notes

This is the P0 keystone: the end-to-end demo (ask -> cast QiMen -> detect -> cited interpretation -> chart) runs through this orchestrator, and its one inviolable rule is that the gateway orchestrates but never computes. Keep the la so envelope read-only here, keep the nine steps explicit and in order, and keep every error in one envelope. The package `tamthuc_api` is shared with TASK-API-002/003/004; they add versioning, rate limiting, and persistence/audit to the same app, so the gateway is one installable, mypy-clean unit. The strategic endpoints ship their contract now and their implementation in P1, so the frontend never has to change its calls when STRAT lands.
