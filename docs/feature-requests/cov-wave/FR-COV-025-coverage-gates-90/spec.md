---
id: COV-025
title: "Raise coverage floors to 90% engines+API and wire gates.env"
module: PLAT
status: ready_to_implement
class: product
priority: SHOULD
phase: P1
lang: rust
effort_h: 12
depends_on: ['COV-001']
refs: ['Grok-38', 'benchmark-claude §5', 'benchmark-grok §8']
created: 2026-07-13
source: coverage-to-100-benchmarks
---

# COV-025 — Raise coverage floors to 90% engines+API and wire gates.env

## Goal

Machine gates fail below 90% on engine crates and tamthuc_api critical modules.

Closes residual gaps from:
- `docs/strategy/claude-docs-coverage-benchmark-2026-07-13.md`
- `docs/strategy/grok-docs-coverage-benchmark-2026-07-13.md`

Existing module FRs marked `done` at package level may already implement partial surfaces; this FR is the **product + acceptance** completion gate for 100% score on those dimensions.

## §1 Acceptance criteria (normative)

1. MUST set COVERAGE_CMD with fail-under 90 for API critical packages.
2. MUST add rust coverage (llvm-cov or tarpaulin) for qimen/ln/thaiat/lichphap.
3. Engine local_fallback paths MUST be exercised in tests.

## §2 Non-goals

- No destiny / prophecy claims (VOICE.md).
- No multi-payment-provider sprawl unless this is COV-026 (single rail only).
- Do not re-open CyberSkill DS for Grok navy mockups.

## §3 Verification

- Unit/integration tests named in implementation.
- Update coverage scores in strategy benchmarks when done (human sets FR `done` only after HITL).
- `bash .cyberos/cuo/gates/run-gates.sh` green where applicable.

## §4 Dependencies

depends_on: COV-001

## §5 Refs

Grok-38, benchmark-claude §5, benchmark-grok §8
