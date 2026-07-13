---
id: COV-001
title: "Oracle certification suite — kinqimen/kinliuren/kintaiyi + jieqi <1′ gate"
module: CORE
status: ready_to_review
class: product
priority: MUST
phase: P0
lang: rust
effort_h: 40
depends_on: ['CORE-006', 'QMDG-006', 'LN-006', 'TAT-006']
refs: ['Claude-02 s8', 'Claude-03 s8', 'Claude-04 s7', 'Claude-05 s6', 'benchmark-claude §5', 'benchmark-grok §7']
created: 2026-07-13
source: coverage-to-100-benchmarks
---

# COV-001 — Oracle certification suite — kinqimen/kinliuren/kintaiyi + jieqi <1′ gate

## Goal

Prove deterministic engines match reference oracles at stated scale; jieqi vs observatory <1 minute on fixed dataset.

Closes residual gaps from:
- `docs/strategy/claude-docs-coverage-benchmark-2026-07-13.md`
- `docs/strategy/grok-docs-coverage-benchmark-2026-07-13.md`

Existing module FRs marked `done` at package level may already implement partial surfaces; this FR is the **product + acceptance** completion gate for 100% score on those dimensions.

## §1 Acceptance criteria (normative)

1. MUST ship golden fixtures: ≥30 QiMen, ≥30 LiuRen, ≥20 TaiYi classical cases with expected ban hashes or key fields.
2. MUST run in CI (cargo test or dedicated oracle job); fail if any mismatch under stamped flags.
3. MUST document oracle versions and flag sets used for each case.
4. MUST include jieqi instant accuracy suite (≥50 terms) with max |error| < 60s vs published ephemeris table.
5. SHALL produce a machine-readable report artefact under docs/status/oracle/.

## §2 Non-goals

- No destiny / prophecy claims (VOICE.md).
- No multi-payment-provider sprawl unless this is COV-026 (single rail only).
- Do not re-open CyberSkill DS for Grok navy mockups.

## §3 Verification

- Unit/integration tests named in implementation.
- Update coverage scores in strategy benchmarks when done (human sets FR `done` only after HITL).
- `bash .cyberos/cuo/gates/run-gates.sh` green where applicable.

## §4 Dependencies

depends_on: CORE-006, QMDG-006, LN-006, TAT-006

## §5 Refs

Claude-02 s8, Claude-03 s8, Claude-04 s7, Claude-05 s6, benchmark-claude §5, benchmark-grok §7
