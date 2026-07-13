---
id: COV-021
title: "Monitoring & alerting productization (metrics, cast latency, error budget)"
module: PLAT
status: done
class: product
priority: SHOULD
phase: P2
lang: python
effort_h: 16
depends_on: ['PLAT-005', 'API-001']
refs: ['Grok-18', 'Grok-41', 'benchmark-grok §8']
created: 2026-07-13
source: coverage-to-100-benchmarks
---

# COV-021 — Monitoring & alerting productization (metrics, cast latency, error budget)

## Goal

Operational visibility for cast p95, error rates, ready failures.

Closes residual gaps from:
- `docs/strategy/claude-docs-coverage-benchmark-2026-07-13.md`
- `docs/strategy/grok-docs-coverage-benchmark-2026-07-13.md`

Existing module FRs marked `done` at package level may already implement partial surfaces; this FR is the **product + acceptance** completion gate for 100% score on those dimensions.

## §1 Acceptance criteria (normative)

1. MUST export metrics for cast latency by system and engine_mode.
2. MUST alert on ready failures when CAST_CLI required.
3. Dashboard or log-based queries documented.

## §2 Non-goals

- No destiny / prophecy claims (VOICE.md).
- No multi-payment-provider sprawl unless this is COV-026 (single rail only).
- Do not re-open CyberSkill DS for Grok navy mockups.

## §3 Verification

- Unit/integration tests named in implementation.
- Update coverage scores in strategy benchmarks when done (human sets FR `done` only after HITL).
- `bash .cyberos/cuo/gates/run-gates.sh` green where applicable.

## §4 Dependencies

depends_on: PLAT-005, API-001

## §5 Refs

Grok-18, Grok-41, benchmark-grok §8
