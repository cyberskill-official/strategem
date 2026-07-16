---
id: COV-023
title: "Report PDF polish + full legal disclaimer block"
module: REPORT
status: done
class: product
priority: SHOULD
phase: P1
lang: python
effort_h: 10
depends_on: ['REPORT-001', 'LEGAL-001']
refs: ['Grok-33', 'Claude-07 s4', 'benchmark-grok Epic6']
created: 2026-07-13
source: coverage-to-100-benchmarks
---

# COV-023 — Report PDF polish + full legal disclaimer block

## Goal

PDF matches product trust ladder and structured sections.

Closes residual gaps from:
- `docs/strategy/claude-docs-coverage-benchmark-2026-07-13.md`
- `docs/strategy/grok-docs-coverage-benchmark-2026-07-13.md`

Existing module tasks marked `done` at package level may already implement partial surfaces; this task is the **product + acceptance** completion gate for 100% score on those dimensions.

## §1 Acceptance criteria (normative)

1. MUST include full disclaimer + AI disclosure on PDF.
2. MUST include chart summary + patterns + recommendations sections.
3. MUST use vernacular pattern names.

## §2 Non-goals

- No destiny / prophecy claims (VOICE.md).
- No multi-payment-provider sprawl unless this is COV-026 (single rail only).
- Do not re-open CyberSkill DS for Grok navy mockups.

## §3 Verification

- Unit/integration tests named in implementation.
- Update coverage scores in strategy benchmarks when done (human sets task `done` only after HITL).
- `bash .cyberos/cuo/gates/run-gates.sh` green where applicable.

## §4 Dependencies

depends_on: REPORT-001, LEGAL-001

## §5 Refs

Grok-33, Claude-07 s4, benchmark-grok Epic6
