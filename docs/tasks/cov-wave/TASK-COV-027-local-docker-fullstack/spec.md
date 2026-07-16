---
id: COV-027
title: "Local full-stack Docker compose — build api+web+cast-cli from source (not GHCR-only)"
module: PLAT
status: done
class: product
priority: MUST
phase: P0
lang: iac
effort_h: 20
depends_on: ['PLAT-004', 'API-001', 'PLAT-013']
refs: ['enterprise-local-objective', 'benchmark-grok §8 ops', 'deploy/README Local']
created: 2026-07-13
source: enterprise-local-docker-lmstudio-objective
---

# COV-027 — Local full-stack Docker compose — build api+web+cast-cli from source (not GHCR-only)

## Goal

A developer (or CI agent) can boot the **full product stack locally from source** with Docker Compose: Postgres, Redis (if required), API (with `cast-cli` for real casts), and web — without depending on pre-pulled GHCR staging images or production secrets. Two consecutive boots produce healthy `/healthz` + `/ready` and a non-empty structured cast for KM/LN/TA.

Closes residual gaps from:
- Enterprise OBJECTIVE: fully worked in local with Docker
- `docs/strategy/grok-docs-coverage-benchmark-2026-07-13.md` ops/local run dimensions
- Staging compose today is GHCR-image-only (`deploy/compose/docker-compose.staging.yml`)

## §1 Acceptance criteria (normative)

1. MUST add `deploy/compose/docker-compose.local.yml` (or equivalent) that **builds** images from `deploy/docker/*.Dockerfile` (or multi-stage local Dockerfiles) rather than requiring GHCR pulls.
2. MUST produce a runnable API image: `python -m tamthuc_api` (or documented entry), `CAST_CLI` points at an in-image `cast-cli` binary built from `crates/cast-cli`, `READY_REQUIRE_CAST_CLI=1` yields `/ready` 200 when CLI is present.
3. MUST expose web on a documented host port (default 3000 or alternate if conflict) with `NEXT_PUBLIC_API_BASE` pointing at the API service (compose network or host-gateway as documented).
4. MUST include Postgres with `DATABASE_URL` wired; app MUST start when DB is healthy (in-memory fallback only when `DATABASE_URL` unset — local compose sets it).
5. MUST document one-command boot + dual-run verification in `docs/deploy/local-docker-lmstudio.md` (shared with COV-028).
6. MUST NOT require production secrets (JWT may use a documented local-dev default; no cloud keys required for cast path).
7. Verification: two independent `compose up` cycles; each cycle proves `/healthz`, `/ready`, and one real cast (KM or LN or TA) with non-empty envelope fields (system plate keys present). Capture logs under operator scratch.

## §2 Non-goals

- Production VPS/Vercel/Supabase secret provisioning (COV-020).
- Replacing GHCR staging compose for remote staging (keep staging file; local is additive).
- Bundling LMStudio inside Docker (host-side; COV-028).

## §3 Verification

- `docker compose -f deploy/compose/docker-compose.local.yml up --build -d` succeeds twice.
- `curl` health/ready + cast API/CLI path with structured JSON body.
- `bash .cyberos/cuo/gates/run-gates.sh` green where Dockerfiles change affect CI lanes.
- Human sets task `done` only after HITL.

## §4 Dependencies

depends_on: PLAT-004, API-001, PLAT-013

## §5 Refs

enterprise-local-objective, benchmark-grok §8 ops, deploy/README Local
