---
id: COV-014
title: "Auto-graded chart practice UI (engine as marker)"
module: EDU
status: ready_to_implement
class: product
priority: MUST
phase: P2
lang: typescript
effort_h: 20
depends_on: ['EDU-002', 'COV-001', 'WEB-002']
refs: ['Claude-07 s3.3', 'benchmark-claude §7']
created: 2026-07-13
source: coverage-to-100-benchmarks
---

# COV-014 — Auto-graded chart practice UI (engine as marker)

## Goal

Step ladder practice graded against engine la so.

Closes residual gaps from:
- `docs/strategy/claude-docs-coverage-benchmark-2026-07-13.md`
- `docs/strategy/grok-docs-coverage-benchmark-2026-07-13.md`

Existing module FRs marked `done` at package level may already implement partial surfaces; this FR is the **product + acceptance** completion gate for 100% score on those dimensions.

## §1 Acceptance criteria (normative)

1. MUST implement practice flow for KM and LN step ladders.
2. MUST show CellDiff messages for wrong seats.
3. MUST never grade interpretation meaning — only deterministic slices.

## §2 Non-goals

- No destiny / prophecy claims (VOICE.md).
- No multi-payment-provider sprawl unless this is COV-026 (single rail only).
- Do not re-open CyberSkill DS for Grok navy mockups.

## §3 Verification

- Unit/integration tests named in implementation.
- Update coverage scores in strategy benchmarks when done (human sets FR `done` only after HITL).
- `bash .cyberos/cuo/gates/run-gates.sh` green where applicable.

## §4 Dependencies

depends_on: EDU-002, COV-001, WEB-002

## §5 Refs

Claude-07 s3.3, benchmark-claude §7
