---
id: COV-024
title: "Playwright full product journeys (home→cast→results→timing→auth)"
module: WEB
status: done
class: product
priority: MUST
phase: P1
lang: typescript
effort_h: 16
depends_on: ['COV-007', 'COV-009', 'WEB-021']
refs: ['Grok-38', 'benchmark-grok §7']
created: 2026-07-13
source: coverage-to-100-benchmarks
---

# COV-024 — Playwright full product journeys (home→cast→results→timing→auth)

## Goal

CI browser gate for critical paths at 1280 and 390 widths.

Closes residual gaps from:
- `docs/strategy/claude-docs-coverage-benchmark-2026-07-13.md`
- `docs/strategy/grok-docs-coverage-benchmark-2026-07-13.md`

Existing module tasks marked `done` at package level may already implement partial surfaces; this task is the **product + acceptance** completion gate for 100% score on those dimensions.

## §1 Acceptance criteria (normative)

1. MUST cover free cast KM/LN, results story region, board toggle.
2. MUST cover timing optimizer page when live.
3. MUST cover login happy path when AUTH productized.
4. CI job MUST run on main PRs.

## §2 Non-goals

- No destiny / prophecy claims (VOICE.md).
- No multi-payment-provider sprawl unless this is COV-026 (single rail only).
- Do not re-open CyberSkill DS for Grok navy mockups.

## §3 Verification

- Unit/integration tests named in implementation.
- Update coverage scores in strategy benchmarks when done (human sets task `done` only after HITL).
- `bash .cyberos/cuo/gates/run-gates.sh` green where applicable.

## §4 Dependencies

depends_on: COV-007, COV-009, WEB-021

## §5 Refs

Grok-38, benchmark-grok §7
