---
id: COV-018
title: "Lunar calendar and Bát tự input modes"
module: WEB
status: done
class: product
priority: SHOULD
phase: P2
lang: typescript
effort_h: 14
depends_on: ['CORE-005', 'WEB-002']
refs: ['Grok-05 s4.1', 'benchmark-grok PRD']
created: 2026-07-13
source: coverage-to-100-benchmarks
---

# COV-018 — Lunar calendar and Bát tự input modes

## Goal

Accept lunar or four-pillar inputs converted via CORE.

Closes residual gaps from:
- `docs/strategy/claude-docs-coverage-benchmark-2026-07-13.md`
- `docs/strategy/grok-docs-coverage-benchmark-2026-07-13.md`

Existing module FRs marked `done` at package level may already implement partial surfaces; this FR is the **product + acceptance** completion gate for 100% score on those dimensions.

## §1 Acceptance criteria (normative)

1. MUST offer input mode: Gregorian | Lunar | Bát tự.
2. MUST convert via CORE without client inventing calendar math.
3. Validation errors in VI.

## §2 Non-goals

- No destiny / prophecy claims (VOICE.md).
- No multi-payment-provider sprawl unless this is COV-026 (single rail only).
- Do not re-open CyberSkill DS for Grok navy mockups.

## §3 Verification

- Unit/integration tests named in implementation.
- Update coverage scores in strategy benchmarks when done (human sets FR `done` only after HITL).
- `bash .cyberos/cuo/gates/run-gates.sh` green where applicable.

## §4 Dependencies

depends_on: CORE-005, WEB-002

## §5 Refs

Grok-05 s4.1, benchmark-grok PRD
