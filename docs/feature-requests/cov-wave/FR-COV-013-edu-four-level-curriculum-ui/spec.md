---
id: COV-013
title: "Four-level curriculum UI wired to EDU-001 data"
module: EDU
status: done
class: product
priority: MUST
phase: P2
lang: typescript
effort_h: 16
depends_on: ['EDU-001', 'WEB-001']
refs: ['Claude-07 s3', 'benchmark-claude §2 tập7']
created: 2026-07-13
source: coverage-to-100-benchmarks
---

# COV-013 — Four-level curriculum UI wired to EDU-001 data

## Goal

Replace flat 3 story modules with L1–L4 progression UI.

Closes residual gaps from:
- `docs/strategy/claude-docs-coverage-benchmark-2026-07-13.md`
- `docs/strategy/grok-docs-coverage-benchmark-2026-07-13.md`

Existing module FRs marked `done` at package level may already implement partial surfaces; this FR is the **product + acceptance** completion gate for 100% score on those dimensions.

## §1 Acceptance criteria (normative)

1. MUST render L1..L4 with prerequisites and criteria from curriculum data.
2. MUST persist learner level locally (or account when AUTH productized).
3. MUST deep-link practice to cast with system.
4. Keep VOICE.md beginner tone; classical names secondary.

## §2 Non-goals

- No destiny / prophecy claims (VOICE.md).
- No multi-payment-provider sprawl unless this is COV-026 (single rail only).
- Do not re-open CyberSkill DS for Grok navy mockups.

## §3 Verification

- Unit/integration tests named in implementation.
- Update coverage scores in strategy benchmarks when done (human sets FR `done` only after HITL).
- `bash .cyberos/cuo/gates/run-gates.sh` green where applicable.

## §4 Dependencies

depends_on: EDU-001, WEB-001

## §5 Refs

Claude-07 s3, benchmark-claude §2 tập7
