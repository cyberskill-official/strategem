---
id: COV-002
title: "Every cast stamps full co_truong_phai + co_lich_phap on envelope"
module: PLAT
status: done
class: product
priority: MUST
phase: P0
lang: rust
effort_h: 12
depends_on: ['PLAT-002', 'CORE-005', 'QMDG-006', 'LN-006', 'TAT-006']
refs: ['Claude-02 s8.2', 'Claude-03 s8.2', 'Claude-05 s6.2', 'strategy 4.3']
created: 2026-07-13
source: coverage-to-100-benchmarks
---

# COV-002 — Every cast stamps full co_truong_phai + co_lich_phap on envelope

## Goal

Reproducibility: identical dau_vao + full flags always rebuilds identical ban.

Closes residual gaps from:
- `docs/strategy/claude-docs-coverage-benchmark-2026-07-13.md`
- `docs/strategy/grok-docs-coverage-benchmark-2026-07-13.md`

Existing module tasks marked `done` at package level may already implement partial surfaces; this task is the **product + acceptance** completion gate for 100% score on those dimensions.

## §1 Acceptance criteria (normative)

1. MUST include complete school + calendar flag objects on every cast-cli and LocalEngineClient envelope.
2. MUST reject silent defaults without stamp (missing flag → explicit default + stamp).
3. MUST expose flags in API chart payload for web technical details.
4. Tests MUST assert stamp keys for all three he values.

## §2 Non-goals

- No destiny / prophecy claims (VOICE.md).
- No multi-payment-provider sprawl unless this is COV-026 (single rail only).
- Do not re-open CyberSkill DS for Grok navy mockups.

## §3 Verification

- Unit/integration tests named in implementation.
- Update coverage scores in strategy benchmarks when done (human sets task `done` only after HITL).
- `bash .cyberos/cuo/gates/run-gates.sh` green where applicable.

## §4 Dependencies

depends_on: PLAT-002, CORE-005, QMDG-006, LN-006, TAT-006

## §5 Refs

Claude-02 s8.2, Claude-03 s8.2, Claude-05 s6.2, strategy 4.3
