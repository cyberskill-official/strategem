---
id: COV-006
title: "TaiYi cach_cuc + chu-khach victory surfaced in API and story"
module: TAT
status: done
class: product
priority: MUST
phase: P1
lang: rust
effort_h: 16
depends_on: ['TAT-005', 'TAT-006', 'WEB-019']
refs: ['Claude-04 s6', 'Claude-04 s7', 'benchmark-claude §2 TAT']
created: 2026-07-13
source: coverage-to-100-benchmarks
---

# COV-006 — TaiYi cach_cuc + chu-khach victory surfaced in API and story

## Goal

No empty-pattern live casts without explicit empty-state; victory criteria readable.

Closes residual gaps from:
- `docs/strategy/claude-docs-coverage-benchmark-2026-07-13.md`
- `docs/strategy/grok-docs-coverage-benchmark-2026-07-13.md`

Existing module tasks marked `done` at package level may already implement partial surfaces; this task is the **product + acceptance** completion gate for 100% score on those dimensions.

## §1 Acceptance criteria (normative)

1. MUST emit non-empty cach_cuc when classical conditions met on golden years.
2. MUST include chu/khach toan and truong_doan in ban always.
3. Story summary MUST use TA metaphor + best pattern or dedicated empty copy.
4. Unit tests for epoch + dem_toan flag combinations.

## §2 Non-goals

- No destiny / prophecy claims (VOICE.md).
- No multi-payment-provider sprawl unless this is COV-026 (single rail only).
- Do not re-open CyberSkill DS for Grok navy mockups.

## §3 Verification

- Unit/integration tests named in implementation.
- Update coverage scores in strategy benchmarks when done (human sets task `done` only after HITL).
- `bash .cyberos/cuo/gates/run-gates.sh` green where applicable.

## §4 Dependencies

depends_on: TAT-005, TAT-006, WEB-019

## §5 Refs

Claude-04 s6, Claude-04 s7, benchmark-claude §2 TAT
