---
id: COV-005
title: "LiuRen nine-school tam truyen branch suite + khoa_the UX"
module: LN
status: ready_to_implement
class: product
priority: MUST
phase: P1
lang: rust
effort_h: 20
depends_on: ['LN-003', 'LN-005', 'LN-006']
refs: ['Claude-02 s4', 'Claude-02 s8', 'benchmark-claude §2 LN']
created: 2026-07-13
source: coverage-to-100-benchmarks
---

# COV-005 — LiuRen nine-school tam truyen branch suite + khoa_the UX

## Goal

Every tong mon branch has unit coverage; khoa the names surface in results.

Closes residual gaps from:
- `docs/strategy/claude-docs-coverage-benchmark-2026-07-13.md`
- `docs/strategy/grok-docs-coverage-benchmark-2026-07-13.md`

Existing module FRs marked `done` at package level may already implement partial surfaces; this FR is the **product + acceptance** completion gate for 100% score on those dimensions.

## §1 Acceptance criteria (normative)

1. MUST add unit tests for all nine tam-truyen decision branches including phuc/phan ngam edges.
2. MUST emit khoa_the array on ban and show in LN chart/results.
3. MUST stamp quy_nhan / truong_sinh flags used.
4. Golden cases MUST cover ≥30 LN casts with tu_khoa + tam_truyen checks.

## §2 Non-goals

- No destiny / prophecy claims (VOICE.md).
- No multi-payment-provider sprawl unless this is COV-026 (single rail only).
- Do not re-open CyberSkill DS for Grok navy mockups.

## §3 Verification

- Unit/integration tests named in implementation.
- Update coverage scores in strategy benchmarks when done (human sets FR `done` only after HITL).
- `bash .cyberos/cuo/gates/run-gates.sh` green where applicable.

## §4 Dependencies

depends_on: LN-003, LN-005, LN-006

## §5 Refs

Claude-02 s4, Claude-02 s8, benchmark-claude §2 LN
