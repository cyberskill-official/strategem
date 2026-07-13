---
id: COV-010
title: "Postgres default persistence for queries/charts/reports in non-test runs"
module: PLAT
status: ready_to_implement
class: product
priority: MUST
phase: P1
lang: python
effort_h: 16
depends_on: ['PLAT-003', 'API-004', 'PLAT-012']
refs: ['Grok-14', 'Claude-06 s1', 'benchmark-grok §7', 'benchmark-claude §3 step9']
created: 2026-07-13
source: coverage-to-100-benchmarks
---

# COV-010 — Postgres default persistence for queries/charts/reports in non-test runs

## Goal

Replace in-memory default when DATABASE_URL is set; docker-compose postgres path works.

Closes residual gaps from:
- `docs/strategy/claude-docs-coverage-benchmark-2026-07-13.md`
- `docs/strategy/grok-docs-coverage-benchmark-2026-07-13.md`

Existing module FRs marked `done` at package level may already implement partial surfaces; this FR is the **product + acceptance** completion gate for 100% score on those dimensions.

## §1 Acceptance criteria (normative)

1. With DATABASE_URL, cast MUST persist query/chart/report and survive process restart.
2. Without DATABASE_URL, MUST fail closed in prod (APP_ENV=production) or explicit dev memory mode.
3. Docker compose service postgres + migrate documented in SHIP_CHECKLIST.
4. Integration test against postgres service in CI (already partial) MUST cover cast→get.

## §2 Non-goals

- No destiny / prophecy claims (VOICE.md).
- No multi-payment-provider sprawl unless this is COV-026 (single rail only).
- Do not re-open CyberSkill DS for Grok navy mockups.

## §3 Verification

- Unit/integration tests named in implementation.
- Update coverage scores in strategy benchmarks when done (human sets FR `done` only after HITL).
- `bash .cyberos/cuo/gates/run-gates.sh` green where applicable.

## §4 Dependencies

depends_on: PLAT-003, API-004, PLAT-012

## §5 Refs

Grok-14, Claude-06 s1, benchmark-grok §7, benchmark-claude §3 step9
