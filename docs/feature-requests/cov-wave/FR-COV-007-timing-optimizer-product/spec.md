---
id: COV-007
title: "Timing Optimizer product path — un-stub API + web page"
module: STRAT
status: ready_to_implement
class: product
priority: MUST
phase: P1
lang: python
effort_h: 24
depends_on: ['STRAT-001', 'QMDG-006', 'WEB-001']
refs: ['Grok-05 s4.3', 'Grok-12', 'Grok-35', 'benchmark-grok §7']
created: 2026-07-13
source: coverage-to-100-benchmarks
---

# COV-007 — Timing Optimizer product path — un-stub API + web page

## Goal

Mount STRAT-001 behind /timing/optimize (not 501) with Next.js page matching product IA.

Closes residual gaps from:
- `docs/strategy/claude-docs-coverage-benchmark-2026-07-13.md`
- `docs/strategy/grok-docs-coverage-benchmark-2026-07-13.md`

Existing module FRs marked `done` at package level may already implement partial surfaces; this FR is the **product + acceptance** completion gate for 100% score on those dimensions.

## §1 Acceptance criteria (normative)

1. API POST /api/v1/timing/optimize MUST return 200 with top windows + scores + reasons (not 501).
2. Web MUST add /timing page: range + question type → ranked list with soft VI copy.
3. MUST use deterministic cast only for scores; AI optional for prose.
4. MUST include disclaimer; no destiny guarantees.
5. E2E smoke MUST cover optimize happy path.

## §2 Non-goals

- No destiny / prophecy claims (VOICE.md).
- No multi-payment-provider sprawl unless this is COV-026 (single rail only).
- Do not re-open CyberSkill DS for Grok navy mockups.

## §3 Verification

- Unit/integration tests named in implementation.
- Update coverage scores in strategy benchmarks when done (human sets FR `done` only after HITL).
- `bash .cyberos/cuo/gates/run-gates.sh` green where applicable.

## §4 Dependencies

depends_on: STRAT-001, QMDG-006, WEB-001

## §5 Refs

Grok-05 s4.3, Grok-12, Grok-35, benchmark-grok §7
