---
id: COV-026
title: "Single payment rail for premium tier (one provider only)"
module: WEB
status: done
class: product
priority: SHOULD
phase: P2
lang: typescript
effort_h: 20
depends_on: ['COV-009', 'AUTH-002']
refs: ['Grok-05 monetization', 'benchmark-grok monetization']
created: 2026-07-13
source: coverage-to-100-benchmarks
---

# COV-026 — Single payment rail for premium tier (one provider only)

> **Supersession (2026-07-26):** Runtime rail is **PayOS** (not Stripe). Historical
> acceptance of this task remains; Stripe identifiers are retired from runtime code,
> env templates, and product copy. See Phase 1 of the VN payments roadmap.

## Goal

Replace pure waitlist for one premium tier with one payment provider.

Closes residual gaps from:
- `docs/strategy/claude-docs-coverage-benchmark-2026-07-13.md`
- `docs/strategy/grok-docs-coverage-benchmark-2026-07-13.md`

Existing module tasks marked `done` at package level may already implement partial surfaces; this task is the **product + acceptance** completion gate for 100% score on those dimensions.

## §1 Acceptance criteria (normative)

1. MUST pick exactly one provider (e.g. Stripe or VNPay) — not multi-rail.
2. MUST map payment success → tier in AUTH RBAC.
3. MUST keep free cast; no destiny claims in paywall copy.
4. Waitlist remains only for advisory human sessions if needed.

## §2 Non-goals

- No destiny / prophecy claims (VOICE.md).
- No multi-payment-provider sprawl unless this is COV-026 (single rail only).
- Do not re-open CyberSkill DS for Grok navy mockups.

## §3 Verification

- Unit/integration tests named in implementation.
- Update coverage scores in strategy benchmarks when done (human sets task `done` only after HITL).
- `bash .cyberos/cuo/gates/run-gates.sh` green where applicable.

## §4 Dependencies

depends_on: COV-009, AUTH-002

## §5 Refs

Grok-05 monetization, benchmark-grok monetization
