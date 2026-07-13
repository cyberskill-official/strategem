---
id: COV-009
title: "Auth product surface — login/signup + session + optional cast gate"
module: AUTH
status: ready_to_implement
class: product
priority: MUST
phase: P1
lang: typescript
effort_h: 28
depends_on: ['AUTH-001', 'AUTH-002', 'WEB-001']
refs: ['Grok-36', 'Grok-05', 'benchmark-grok §7', 'benchmark-claude §3 step2']
created: 2026-07-13
source: coverage-to-100-benchmarks
---

# COV-009 — Auth product surface — login/signup + session + optional cast gate

## Goal

Ship login UI over existing JWT package; free cast may remain open but account unlocks sync.

Closes residual gaps from:
- `docs/strategy/claude-docs-coverage-benchmark-2026-07-13.md`
- `docs/strategy/grok-docs-coverage-benchmark-2026-07-13.md`

Existing module FRs marked `done` at package level may already implement partial surfaces; this FR is the **product + acceptance** completion gate for 100% score on those dimensions.

## §1 Acceptance criteria (normative)

1. MUST provide /login and /signup (or modal) with email+password; social MAY follow.
2. MUST store refresh session securely (httpOnly cookie preferred).
3. Dashboard history MUST sync when authenticated; local pins remain offline fallback.
4. RBAC tiers MUST gate premium features (timing depth / report PDF batch) without breaking free cast.
5. Birth data fields MUST encrypt at rest when stored (AUTH-001).

## §2 Non-goals

- No destiny / prophecy claims (VOICE.md).
- No multi-payment-provider sprawl unless this is COV-026 (single rail only).
- Do not re-open CyberSkill DS for Grok navy mockups.

## §3 Verification

- Unit/integration tests named in implementation.
- Update coverage scores in strategy benchmarks when done (human sets FR `done` only after HITL).
- `bash .cyberos/cuo/gates/run-gates.sh` green where applicable.

## §4 Dependencies

depends_on: AUTH-001, AUTH-002, WEB-001

## §5 Refs

Grok-36, Grok-05, benchmark-grok §7, benchmark-claude §3 step2
