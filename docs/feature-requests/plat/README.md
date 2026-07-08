# PLAT - platform, infra, ops

The platform floor the whole product runs on: the hybrid monorepo, the la so JSON envelope contract, the DB and its row-level security, the CI/CD pipeline, and the P1-P2 hardening (observability, caching, security, resilience, backup/DR, infra-as-code). 10 FRs, ~100 engineering-hours, P0 floor then P1-P2 hardening. Source of rationale: `../../strategy/tam-thuc-unified-plan-2026-07-08.md` (sections 3.2 DEC-2, 4.1, 4.3, 4.4, RISK-5/6/8) and Grok 21,22,27,39,41,47,48,50. Implementation order and trigger: `../IMPLEMENTATION_ORDER.md` + `../PROMPT.md`.

PLAT is where the hybrid-stack decision (DEC-2) is made real: a Rust cargo workspace, uv-managed Python packages, and a Next.js app in one repo, bound to the AI branch through one versioned contract (the la so envelope) and gated by one CI/CD train. Everything else in the catalog stands on this floor.

## FR list

| FR | Pri | Phase | h | depends_on | Spec | Title |
|---|---|---|--:|---|---|---|
| PLAT-001 | MUST | P0 | 12 | - | [FR-PLAT-001](FR-PLAT-001-monorepo-workspace.md) | Monorepo + hybrid workspace (cargo + uv + Next.js) + CI skeleton |
| PLAT-002 | MUST | P0 | 10 | PLAT-001 | [FR-PLAT-002](FR-PLAT-002-la-so-json-envelope.md) | La so JSON envelope contract (Rust+Python shared types, versioned, contract test) |
| PLAT-003 | MUST | P0 | 12 | PLAT-001 | [FR-PLAT-003](FR-PLAT-003-db-schema-migrations.md) | DB schema + migrations + RLS + indexes (users/queries/charts/patterns/reports/audit) |
| PLAT-004 | MUST | P0 | 10 | PLAT-001 | [FR-PLAT-004](FR-PLAT-004-cicd-pipeline.md) | CI/CD pipeline (lint/type/test, docker, security scan, staging->prod gate) |
| PLAT-005 | MUST | P1 | 10 | PLAT-004 | (planned) | Observability (Prometheus/Grafana, Sentry, structured logs, alerting) |
| PLAT-006 | SHOULD | P1 | 8 | PLAT-003 | (planned) | Redis caching (chart cache 24h TTL, invalidation, warming) |
| PLAT-007 | MUST | P1 | 12 | PLAT-004, AUTH-002 | (planned) | Security hardening (STRIDE controls, TLS 1.3, secrets, dep scan) |
| PLAT-008 | MUST | P1 | 8 | PLAT-005 | (planned) | Resilience (circuit breaker, retry/backoff, graceful degradation) |
| PLAT-009 | SHOULD | P2 | 8 | PLAT-003 | (planned) | Backup + DR (daily backup, PITR, RPO 1h / RTO 4h, restore drill) |
| PLAT-010 | SHOULD | P2 | 10 | PLAT-004 | (planned) | Infra as code (Terraform + K8s manifests, autoscaling) |

Four are authored in full: PLAT-001 (the monorepo + hybrid workspace + CI skeleton), PLAT-002 (the la so envelope, the cross-language contract), PLAT-003 (the DB schema + fail-closed RLS), and PLAT-004 (the CI/CD pipeline). Six are listed for the dependency picture and authored later: PLAT-005 (observability, P1), PLAT-006 (Redis chart cache, P1), PLAT-007 (STRIDE security hardening, P1), PLAT-008 (resilience, P1), PLAT-009 (backup/DR, P2), and PLAT-010 (Terraform + K8s, P2).

## Internal build order

```
PLAT-001 (monorepo + hybrid workspace + CI skeleton)
  -> PLAT-002 (la so envelope contract - Rust + Python shared types)
  -> PLAT-003 (DB schema + migrations + fail-closed RLS + GIN indexes)
  -> PLAT-004 (CI/CD pipeline: extends the CI skeleton with docker + scan + staging->prod gate)
       -> PLAT-005 (observability) -> PLAT-008 (resilience)
       -> PLAT-007 (security hardening; also needs AUTH-002)
  PLAT-003 -> PLAT-006 (Redis chart cache) ; PLAT-003 -> PLAT-009 (backup/DR)
  PLAT-004 -> PLAT-010 (infra as code)
```

PLAT-001 is the root of the whole program (it depends on nothing). PLAT-002/003/004 are the three P0 pillars on top of it; the P1-P2 FRs harden the running system.

## Cross-module dependencies

- Blocks essentially everything: PLAT-001 hosts every crate, package, and app; PLAT-002 is (de)serialized by every engine and the interpretation branch (`blocks` every engine assembly FR and RAG); PLAT-003 backs RULE-001, API-004, AUTH-001, and the cache; PLAT-004 is the train every deploy rides.
- The la so envelope (PLAT-002) is the one cross-language contract: the Rust engines (CORE, QMDG, LN, TAT) emit it and the Python branch (RULE consumers, RAG, REPORT, API) reads it. FR-CORE-005's calendar output IS the `lich_phap` sub-object; the two are one contract seen from two sides.
- The DB (PLAT-003) is the data tier for AUTH (users), API (queries/charts/reports/audit persistence, FR-API-004), and RULE/KB (`knowledge_patterns`), with the erasure/export contracts of FR-LEGAL-002 operating on the same schema.
- Security (PLAT-007) depends on AUTH-002 (the tier/RBAC model it hardens) and is enforced through the PLAT-004 pipeline (the security scan and secret sourcing).

## Module notes

- Hybrid stack per DEC-2 (strategy 3.2): Rust engines and rule detection under `crates/`, Python AI/RAG/orchestration/report under `packages/` (uv), Next.js frontend under `apps/web`. PLAT-001 establishes the three-toolchain workspace and gates all three lanes from the first commit; the layout mirrors the cyberos convention (DEC-1) so a later absorption is mechanical. The lang mix within the module reflects this: PLAT-001/003/004 are iac-flavored, PLAT-002/006/008 are Rust, the rest are infra/ops.
- The la so envelope (PLAT-002) is the cross-language contract, and it is the thing that makes the hybrid stack safe: it is a versioned JSON Schema with generated Rust serde types and Python Pydantic models, contract-tested on both sides so a drift is a failing CI check, not a production incident (RISK-8). Treat any change to the chart shape as a PLAT-002 versioned change, never a local edit in an engine or a screen.
- RLS is fail-closed (PLAT-003): every user-scoped table has `ENABLE` + `FORCE ROW LEVEL SECURITY`, denies by default, and is visible only through an explicit policy bound to a per-request session variable the app sets from the authenticated principal. A connection that forgets the variable sees zero rows, never all rows. This is the cyberos pattern, chosen because the data is personal divination data (RISK-5); the isolation test is a required CI gate.
- Security is STRIDE-modeled (PLAT-007): the threat model drives the control set (TLS 1.3, secrets management, dependency scanning, the auth/tier hardening), and the controls are enforced through the PLAT-004 pipeline - the security scan fails the build on a high/critical finding, overridable only by a reviewable allowlist. Oracle libraries are CI references, never embedded runtime deps (RISK-6), so their licenses never enter the shipped artifact.
- The CI/CD pipeline (PLAT-004) keeps a human in the loop for production: staging auto-deploys, production is behind a required-reviewer approval gate - the same human-in-the-loop principle the interpretation layer uses (strategy 4.4), applied to releasing a legally sensitive surface (RISK-4).
