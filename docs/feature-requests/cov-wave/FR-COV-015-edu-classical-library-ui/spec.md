---
id: COV-015
title: "Bilingual classical library reader UI"
module: EDU
status: ready_to_implement
class: product
priority: MUST
phase: P2
lang: typescript
effort_h: 14
depends_on: ['EDU-003', 'KB-003']
refs: ['Claude-07 s3.3', 'Claude-06 s4.2', 'benchmark-claude §7']
created: 2026-07-13
source: coverage-to-100-benchmarks
---

# COV-015 — Bilingual classical library reader UI

## Goal

Search/read Han + bạch thoại + dich with live citations.

Closes residual gaps from:
- `docs/strategy/claude-docs-coverage-benchmark-2026-07-13.md`
- `docs/strategy/grok-docs-coverage-benchmark-2026-07-13.md`

Existing module FRs marked `done` at package level may already implement partial surfaces; this FR is the **product + acceptance** completion gate for 100% score on those dimensions.

## §1 Acceptance criteria (normative)

1. MUST show three layers; never drop Han.
2. MUST resolve citation id from results to passage.
3. MUST respect diacritic/Han line-height (no clip).

## §2 Non-goals

- No destiny / prophecy claims (VOICE.md).
- No multi-payment-provider sprawl unless this is COV-026 (single rail only).
- Do not re-open CyberSkill DS for Grok navy mockups.

## §3 Verification

- Unit/integration tests named in implementation.
- Update coverage scores in strategy benchmarks when done (human sets FR `done` only after HITL).
- `bash .cyberos/cuo/gates/run-gates.sh` green where applicable.

## §4 Dependencies

depends_on: EDU-003, KB-003

## §5 Refs

Claude-07 s3.3, Claude-06 s4.2, benchmark-claude §7
