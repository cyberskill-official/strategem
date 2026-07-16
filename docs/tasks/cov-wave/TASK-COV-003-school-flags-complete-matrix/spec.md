---
id: COV-003
title: "Complete school-flag matrix UI (maoshan, zhong_gong_ky, dem_toan, …)"
module: WEB
status: done
class: product
priority: MUST
phase: P0
lang: typescript
effort_h: 10
depends_on: ['COV-002']
refs: ['Claude-03 s8.2', 'Claude-04 s7.2', 'benchmark-claude §4']
created: 2026-07-13
source: coverage-to-100-benchmarks
---

# COV-003 — Complete school-flag matrix UI (maoshan, zhong_gong_ky, dem_toan, …)

## Goal

Close Claude flag-table gaps so every engine-critical flag is operator-configurable.

Closes residual gaps from:
- `docs/strategy/claude-docs-coverage-benchmark-2026-07-13.md`
- `docs/strategy/grok-docs-coverage-benchmark-2026-07-13.md`

Existing module tasks marked `done` at package level may already implement partial surfaces; this task is the **product + acceptance** completion gate for 100% score on those dimensions.

## §1 Acceptance criteria (normative)

1. MUST add dingju maoshan (or document unsupported with engine refuse).
2. MUST add zhong_gong_ky and dem_toan (or engine-equivalent names) to school-flags form.
3. MUST show human VI labels + short descriptions; never English-only chrome in vi locale.
4. MUST pass flags through cast payload and reappear stamped on results tech details.

## §2 Non-goals

- No destiny / prophecy claims (VOICE.md).
- No multi-payment-provider sprawl unless this is COV-026 (single rail only).
- Do not re-open CyberSkill DS for Grok navy mockups.

## §3 Verification

- Unit/integration tests named in implementation.
- Update coverage scores in strategy benchmarks when done (human sets task `done` only after HITL).
- `bash .cyberos/cuo/gates/run-gates.sh` green where applicable.

## §4 Dependencies

depends_on: COV-002

## §5 Refs

Claude-03 s8.2, Claude-04 s7.2, benchmark-claude §4
