---
id: COV-020
title: "Staging deploy wiring — Vercel + VPS API + Supabase linked runbook"
module: PLAT
status: ready_to_implement
class: product
priority: MUST
phase: P1
lang: iac
effort_h: 20
depends_on: ['PLAT-011', 'PLAT-012', 'PLAT-013', 'PLAT-014', 'COV-010']
refs: ['Grok-39', 'benchmark-grok §7', 'SHIP_CHECKLIST']
created: 2026-07-13
source: coverage-to-100-benchmarks
---

# COV-020 — Staging deploy wiring — Vercel + VPS API + Supabase linked runbook

## Goal

Documented and automatable staging: web→api→db with CAST_CLI and READY_REQUIRE_CAST_CLI.

Closes residual gaps from:
- `docs/strategy/claude-docs-coverage-benchmark-2026-07-13.md`
- `docs/strategy/grok-docs-coverage-benchmark-2026-07-13.md`

Existing module FRs marked `done` at package level may already implement partial surfaces; this FR is the **product + acceptance** completion gate for 100% score on those dimensions.

## §1 Acceptance criteria (normative)

1. MUST provide compose or runbooks for postgres+api+web staging.
2. MUST set health/ready checks; READY_REQUIRE_CAST_CLI=1 in staging/prod.
3. MUST verify CORS + NEXT_PUBLIC_API_BASE.
4. Smoke script MUST cast KM/LN/TA against staging URL.
5. Secrets stay out of git; checklist only.

## §2 Non-goals

- No destiny / prophecy claims (VOICE.md).
- No multi-payment-provider sprawl unless this is COV-026 (single rail only).
- Do not re-open CyberSkill DS for Grok navy mockups.

## §3 Verification

- Unit/integration tests named in implementation.
- Update coverage scores in strategy benchmarks when done (human sets FR `done` only after HITL).
- `bash .cyberos/cuo/gates/run-gates.sh` green where applicable.

## §4 Dependencies

depends_on: PLAT-011, PLAT-012, PLAT-013, PLAT-014, COV-010

## §5 Refs

Grok-39, benchmark-grok §7, SHIP_CHECKLIST
