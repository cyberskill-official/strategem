# API - gateway and orchestration

The FastAPI gateway that fronts the whole platform: it authenticates and authorizes a request, runs the nine-step query flow that joins the deterministic engine branch to the interpretation branch, enforces per-tier rate limits, persists the result, and returns one structured shape on success and one structured envelope on error. It is the single entry point the frontend and any SDK talk to. Language is Python / FastAPI (DEC-2); everything lives in one package, `tamthuc_api`. Primary sources: Grok 06 (backend spec, endpoint list), Grok 12 (API reference, rate limits), Grok 49 (versioning). See the unified plan sections 4.1-4.4.

## tasks

| task | Pri | Phase | h | Title |
|---|---|---|--:|---|
| API-001 | MUST | P0 | 14 | [Query orchestration + endpoint contracts (calculate/*, error envelope)](TASK-API-001-query-orchestration/spec.md) |
| API-002 | SHOULD | P1 | 6 | API versioning + deprecation policy (URL v1, header) |
| API-003 | MUST | P0 | 8 | [Rate limiting + abuse detection (per tier)](TASK-API-003-rate-limiting/spec.md) |
| API-004 | MUST | P0 | 8 | [Query/chart/report persistence + audit rows](TASK-API-004-persistence-audit/spec.md) |
| API-005 | SHOULD | P1 | 4 | [Patterns `?system=` filter contract lock](TASK-API-005-patterns-system-filter/spec.md) |

Three P0 tasks are authored (API-001 the orchestrator + contracts, API-003 rate limiting + abuse, API-004 persistence + audit). Also authored: API-002 (URL-`v1` plus header API versioning and the deprecation policy, P1) and API-005 (patterns `?system=` filter contract lock / live-audit truth-up, P1 improvement).

## Internal spine

```
API-001 (FastAPI app + 9-step orchestrator + endpoint contracts + structured error envelope)
   -> API-003 (per-tier rate limiting + abuse detection; middleware on the metered routes)  [needs AUTH-002]
   -> API-004 (step 9: persist query/chart/report + append-only audit rows)  [needs PLAT-003]
   -> API-002 (versioning + deprecation policy; P1)
```

## Cross-module dependencies

- Depends on AUTH-001 (the auth dependency and the mounted `/auth/*` routes) and CORE-005 (the calendar context resolved at step 2). API-003 depends on AUTH-002 (tier + quota config); API-004 depends on PLAT-003 (the physical tables + RLS).
- Orchestrates the core branches: it calls CORE for the calendar context, the engine(s) (TASK-QMDG-006, later TASK-LN-006 / TASK-TAT-006) to cast, TASK-RULE-003 to detect patterns, TASK-RAG-003 to interpret, and TASK-REPORT-001 to assemble - reading the TASK-PLAT-002 la so envelope but never mutating it.
- Blocks the frontend and the plan controls: TASK-WEB-002 (the query input screen) calls `/calculate/*`; TASK-API-003's limits are the cost/abuse gate on those endpoints; TASK-API-004's store feeds TASK-RAG-004 (human review), TASK-AUTH-004 (DSAR), and TASK-LEGAL-002 (retention). Uses TASK-PLAT-006 Redis for rate-limit counters and coordinates upstream-failure handling with TASK-PLAT-008.

## Module notes

- The gateway orchestrates but never computes. The one inviolable rule: the API runs the nine-step flow (auth -> CORE calendar -> engine cast -> RULE detect -> RAG retrieve + interpret -> report -> return -> persist) but never re-computes or mutates a chart. It passes the engine's la so JSON envelope to RULE and RAG read-only, and asserts the returned envelope is byte-identical to the cast one. The moment the gateway could re-derive an engine field, determinism and reproducibility would be gone (strategy 4.3, RISK-8). Persistence stores the envelope verbatim, so the read-only invariant holds end to end and at rest.
- One structured error envelope, standard HTTP codes. Every failure returns `{ error: { code, message, details, request_id } }` with the correct status (400/401/403/404/422/429/500/501/502/503). The frontend, the SDK, and the operator dashboards parse one shape; `code` carries the fine signal, the HTTP status the coarse one. Central exception handlers render it, so no route emits an ad hoc error body.
- Auth, tiers, and limits are enforced, not advertised. JWT Bearer for user principals, API key for Enterprise; per-tier quotas (Free 100/day, Premium 5000/day, Enterprise custom) enforced from the single AUTH-002 config, on an LLM-backed endpoint where an unmetered request is a direct cost and abuse surface. The limiter fails safe (a datastore outage degrades to a conservative cap, never to unlimited).
- AIDisclosure is carried through, never stripped. Every response bearing interpretation carries the AIDisclosure block from TASK-RAG-003; the gateway passes it through and the response contract requires it. No endpoint returns a medical, legal, or financial verdict (strategy 7).
- One package, one installable unit. All four tasks extend the same `tamthuc_api` FastAPI app (orchestrator, routes, clients, ratelimit, abuse, persistence, audit, versioning modules), so the gateway is one mypy-clean, pytest-covered Python package.
