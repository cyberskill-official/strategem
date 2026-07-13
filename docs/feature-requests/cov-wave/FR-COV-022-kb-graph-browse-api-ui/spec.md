---
id: COV-022
title: "Knowledge-graph browse API + lightweight explorer UI"
module: KB
status: done
class: product
priority: COULD
phase: P2
lang: python
effort_h: 16
depends_on: ['KB-001', 'KB-005']
refs: ['Claude-06 s3', 'benchmark-claude §2 tập6']
created: 2026-07-13
source: coverage-to-100-benchmarks
---

# COV-022 — Knowledge-graph browse API + lightweight explorer UI

## Goal

Traverse ngũ hành / chi relations for learner and RAG expand.

Closes residual gaps from:
- `docs/strategy/claude-docs-coverage-benchmark-2026-07-13.md`
- `docs/strategy/grok-docs-coverage-benchmark-2026-07-13.md`

Existing module FRs marked `done` at package level may already implement partial surfaces; this FR is the **product + acceptance** completion gate for 100% score on those dimensions.

## §1 Acceptance criteria (normative)

1. MUST expose graph query endpoints for node neighbors by type.
2. MUST ship minimal explorer under /learn/graph or admin.
3. MUST not invent edges; only stored graph.

## §2 Non-goals

- No destiny / prophecy claims (VOICE.md).
- No multi-payment-provider sprawl unless this is COV-026 (single rail only).
- Do not re-open CyberSkill DS for Grok navy mockups.

## §3 Verification

- Unit/integration tests named in implementation.
- Update coverage scores in strategy benchmarks when done (human sets FR `done` only after HITL).
- `bash .cyberos/cuo/gates/run-gates.sh` green where applicable.

## §4 Dependencies

depends_on: KB-001, KB-005

## §5 Refs

Claude-06 s3, benchmark-claude §2 tập6
