---
id: COV-012
title: "Cross-system validation UI (calculate/all + consensus view)"
module: STRAT
status: done
class: product
priority: SHOULD
phase: P1
lang: typescript
effort_h: 14
depends_on: ['STRAT-004', 'API-001', 'WEB-003']
refs: ['Grok-05 s4.2', 'benchmark-grok Epic4']
created: 2026-07-13
source: coverage-to-100-benchmarks
---

# COV-012 — Cross-system validation UI (calculate/all + consensus view)

## Goal

User can cast all three systems and see consensus/divergence.

Closes residual gaps from:
- `docs/strategy/claude-docs-coverage-benchmark-2026-07-13.md`
- `docs/strategy/grok-docs-coverage-benchmark-2026-07-13.md`

Existing module tasks marked `done` at package level may already implement partial surfaces; this task is the **product + acceptance** completion gate for 100% score on those dimensions.

## §1 Acceptance criteria (normative)

1. MUST call calculate/all or parallel calculate.
2. UI MUST show three columns or tabs with soft consensus summary.
3. MUST NOT invent numbers; only compare engine outputs.

## §2 Non-goals

- No destiny / prophecy claims (VOICE.md).
- No multi-payment-provider sprawl unless this is COV-026 (single rail only).
- Do not re-open CyberSkill DS for Grok navy mockups.

## §3 Verification

- Unit/integration tests named in implementation.
- Update coverage scores in strategy benchmarks when done (human sets task `done` only after HITL).
- `bash .cyberos/cuo/gates/run-gates.sh` green where applicable.

## §4 Dependencies

depends_on: STRAT-004, API-001, WEB-003

## §5 Refs

Grok-05 s4.2, benchmark-grok Epic4
