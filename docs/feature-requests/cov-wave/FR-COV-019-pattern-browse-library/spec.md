---
id: COV-019
title: "Searchable pattern library (top seeds across 3 systems)"
module: WEB
status: done
class: product
priority: SHOULD
phase: P1
lang: typescript
effort_h: 10
depends_on: ['KB-002', 'RULE-001']
refs: ['Grok-17', 'Claude-03 s7', 'benchmark-grok Epic3']
created: 2026-07-13
source: coverage-to-100-benchmarks
---

# COV-019 — Searchable pattern library (top seeds across 3 systems)

## Goal

Browse/search ≥150 seeded patterns with citations.

Closes residual gaps from:
- `docs/strategy/claude-docs-coverage-benchmark-2026-07-13.md`
- `docs/strategy/grok-docs-coverage-benchmark-2026-07-13.md`

Existing module FRs marked `done` at package level may already implement partial surfaces; this FR is the **product + acceptance** completion gate for 100% score on those dimensions.

## §1 Acceptance criteria (normative)

1. MUST list patterns from knowledge API/seed with filters by he.
2. MUST show vernacular + Han + short gloss + citation link.
3. No prophecy wording in descriptions.

## §2 Non-goals

- No destiny / prophecy claims (VOICE.md).
- No multi-payment-provider sprawl unless this is COV-026 (single rail only).
- Do not re-open CyberSkill DS for Grok navy mockups.

## §3 Verification

- Unit/integration tests named in implementation.
- Update coverage scores in strategy benchmarks when done (human sets FR `done` only after HITL).
- `bash .cyberos/cuo/gates/run-gates.sh` green where applicable.

## §4 Dependencies

depends_on: KB-002, RULE-001

## §5 Refs

Grok-17, Claude-03 s7, benchmark-grok Epic3
