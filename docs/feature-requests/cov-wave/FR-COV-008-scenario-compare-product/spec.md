---
id: COV-008
title: "Scenario comparison product path — un-stub API + web page"
module: STRAT
status: done
class: product
priority: MUST
phase: P1
lang: python
effort_h: 16
depends_on: ['STRAT-002', 'COV-007']
refs: ['Grok-05 s4.3', 'Grok mockup Scenario Comparison', 'benchmark-grok §7']
created: 2026-07-13
source: coverage-to-100-benchmarks
---

# COV-008 — Scenario comparison product path — un-stub API + web page

## Goal

Side-by-side date/option compare for the same decision.

Closes residual gaps from:
- `docs/strategy/claude-docs-coverage-benchmark-2026-07-13.md`
- `docs/strategy/grok-docs-coverage-benchmark-2026-07-13.md`

Existing module FRs marked `done` at package level may already implement partial surfaces; this FR is the **product + acceptance** completion gate for 100% score on those dimensions.

## §1 Acceptance criteria (normative)

1. API POST /api/v1/scenario/compare MUST return 200 (not 501).
2. Web MUST add /scenarios page: 2–4 candidates, side-by-side windows.
3. MUST reuse Timing Optimizer scoring; no double-cast inventing numbers.
4. VI labels beginner-safe.

## §2 Non-goals

- No destiny / prophecy claims (VOICE.md).
- No multi-payment-provider sprawl unless this is COV-026 (single rail only).
- Do not re-open CyberSkill DS for Grok navy mockups.

## §3 Verification

- Unit/integration tests named in implementation.
- Update coverage scores in strategy benchmarks when done (human sets FR `done` only after HITL).
- `bash .cyberos/cuo/gates/run-gates.sh` green where applicable.

## §4 Dependencies

depends_on: STRAT-002, COV-007

## §5 Refs

Grok-05 s4.3, Grok mockup Scenario Comparison, benchmark-grok §7
