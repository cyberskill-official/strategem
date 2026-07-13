---
id: COV-016
title: "First-run onboarding + help center product"
module: EDU
status: ready_to_implement
class: product
priority: SHOULD
phase: P2
lang: typescript
effort_h: 12
depends_on: ['EDU-004', 'LEGAL-001', 'WEB-001']
refs: ['Grok-17', 'Grok-42', 'Claude-07 s2.2', 'benchmark-grok Epic5']
created: 2026-07-13
source: coverage-to-100-benchmarks
---

# COV-016 — First-run onboarding + help center product

## Goal

Teach cast-read-decide and disclosure components once.

Closes residual gaps from:
- `docs/strategy/claude-docs-coverage-benchmark-2026-07-13.md`
- `docs/strategy/grok-docs-coverage-benchmark-2026-07-13.md`

Existing module FRs marked `done` at package level may already implement partial surfaces; this FR is the **product + acceptance** completion gate for 100% score on those dimensions.

## §1 Acceptance criteria (normative)

1. MUST run first-run onboarding (skippable, re-openable).
2. MUST explain AIDisclosure + HumanReview in plain VI.
3. MUST ship searchable help articles catalog.

## §2 Non-goals

- No destiny / prophecy claims (VOICE.md).
- No multi-payment-provider sprawl unless this is COV-026 (single rail only).
- Do not re-open CyberSkill DS for Grok navy mockups.

## §3 Verification

- Unit/integration tests named in implementation.
- Update coverage scores in strategy benchmarks when done (human sets FR `done` only after HITL).
- `bash .cyberos/cuo/gates/run-gates.sh` green where applicable.

## §4 Dependencies

depends_on: EDU-004, LEGAL-001, WEB-001

## §5 Refs

Grok-17, Grok-42, Claude-07 s2.2, benchmark-grok Epic5
