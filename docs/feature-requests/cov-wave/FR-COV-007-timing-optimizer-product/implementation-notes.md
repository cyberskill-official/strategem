# COV-007 implementation notes

## Landed

| artefact | path |
|----------|------|
| API mount STRAT-001 | `packages/tamthuc_api/src/tamthuc_api/routes/timing.py` |
| API tests | `packages/tamthuc_api/tests/test_timing_optimize_cov007.py` |
| Web page | `apps/web/app/timing/page.tsx` |
| Nav + dashboard flow | `top-bar.tsx`, `flow-entry-cards.tsx` |
| i18n | `vi.json` / `en.json` / `zh.json` |
| Page smoke | `apps/web/tests/timing-page.test.mjs` |
| E2E smoke | `apps/web/tests/e2e-live-smoke.mjs` (optimize happy path) |
| Dep | `tamthuc-api` → `tamthuc-strat` workspace |

## Behaviour

- `POST /api/v1/timing/optimize` → 200 with `windows[]` (score, cast_ref, reasons, cat/hung), disclaimer, honest non-LLM disclosure.
- Engine cast per window via orchestrator `engine.cast("qimen", …)` — no plate math in STRAT.
- Web `/timing`: range + question type → ranked list with soft VI copy + disclaimer.

## Tests

| suite | result |
|-------|--------|
| test_timing_optimize_cov007 | pass |
| tamthuc_strat timing_optimizer | pass |
| timing-page.test.mjs | pass |

## Status

`ready_to_review` — **HITL required**. Agent will not set `done`.
