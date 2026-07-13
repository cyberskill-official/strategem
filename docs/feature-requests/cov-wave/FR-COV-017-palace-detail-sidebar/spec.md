---
id: COV-017
title: "Palace/detail sidebar for interactive charts"
module: CHART
status: done
class: product
priority: SHOULD
phase: P1
lang: typescript
effort_h: 12
depends_on: ['CHART-001', 'CHART-002', 'CHART-003']
refs: ['Grok-07 s3', 'Claude-07 s5.2', 'benchmark-grok UI']
created: 2026-07-13
source: coverage-to-100-benchmarks
---

# COV-017 — Palace/detail sidebar for interactive charts

## Goal

Click cung → sidebar with stem/star/door/god + related patterns.

Closes residual gaps from:
- `docs/strategy/claude-docs-coverage-benchmark-2026-07-13.md`
- `docs/strategy/grok-docs-coverage-benchmark-2026-07-13.md`

Existing module FRs marked `done` at package level may already implement partial surfaces; this FR is the **product + acceptance** completion gate for 100% score on those dimensions.

## §1 Acceptance criteria (normative)

1. MUST show detail panel on palace select for KM; LN/TA analogous.
2. MUST list related patterns for that seat when available.
3. Keyboard accessible; ARIA labels preserved.

## §2 Non-goals

- No destiny / prophecy claims (VOICE.md).
- No multi-payment-provider sprawl unless this is COV-026 (single rail only).
- Do not re-open CyberSkill DS for Grok navy mockups.

## §3 Verification

- Unit/integration tests named in implementation.
- Update coverage scores in strategy benchmarks when done (human sets FR `done` only after HITL).
- `bash .cyberos/cuo/gates/run-gates.sh` green where applicable.

## §4 Dependencies

depends_on: CHART-001, CHART-002, CHART-003

## §5 Refs

Grok-07 s3, Claude-07 s5.2, benchmark-grok UI
