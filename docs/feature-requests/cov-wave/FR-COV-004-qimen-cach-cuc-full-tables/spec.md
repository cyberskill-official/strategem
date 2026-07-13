---
id: COV-004
title: "QiMen full cat/hung cach_cuc tables as pattern-as-data + detection coverage"
module: QMDG
status: done
class: product
priority: MUST
phase: P0
lang: rust
effort_h: 24
depends_on: ['QMDG-005', 'RULE-003', 'KB-002']
refs: ['Claude-03 s7', 'Grok-31', 'benchmark-claude §2 QMDG']
created: 2026-07-13
source: coverage-to-100-benchmarks
---

# COV-004 — QiMen full cat/hung cach_cuc tables as pattern-as-data + detection coverage

## Goal

Productize Claude cat/hung tables beyond sparse live patterns.

Closes residual gaps from:
- `docs/strategy/claude-docs-coverage-benchmark-2026-07-13.md`
- `docs/strategy/grok-docs-coverage-benchmark-2026-07-13.md`

Existing module FRs marked `done` at package level may already implement partial surfaces; this FR is the **product + acceptance** completion gate for 100% score on those dimensions.

## §1 Acceptance criteria (normative)

1. MUST seed ≥40 named QiMen patterns with conditions + citations.
2. MUST detect ≥15 high-priority patterns on golden fixtures with unit tests.
3. MUST NOT invent polarity without rule match.
4. Web MUST display vernacular names first (no raw engine ids as primary).

## §2 Non-goals

- No destiny / prophecy claims (VOICE.md).
- No multi-payment-provider sprawl unless this is COV-026 (single rail only).
- Do not re-open CyberSkill DS for Grok navy mockups.

## §3 Verification

- Unit/integration tests named in implementation.
- Update coverage scores in strategy benchmarks when done (human sets FR `done` only after HITL).
- `bash .cyberos/cuo/gates/run-gates.sh` green where applicable.

## §4 Dependencies

depends_on: QMDG-005, RULE-003, KB-002

## §5 Refs

Claude-03 s7, Grok-31, benchmark-claude §2 QMDG
