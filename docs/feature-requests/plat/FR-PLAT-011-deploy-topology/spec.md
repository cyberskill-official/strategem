---
id: FR-PLAT-011
title: "Deploy topology SoT - Vercel for user web (apps/web), Supabase for Postgres (schema + RLS), custom VPS for backend API and engine images; one push, three surfaces"
module: PLAT
priority: MUST
status: done
phase: P3
slice: 1
lang: iac
effort_h: 6
owner: Stephen Cheng (Founder/CPO)
created: 2026-07-13
refs: [cyberos docs/deploy/web-and-desktop-deploy.md, cyberos deploy/vps, strategy 4.1]
related_frs: [FR-PLAT-003, FR-PLAT-004, FR-PLAT-010, FR-PLAT-012, FR-PLAT-013, FR-PLAT-014, FR-PLAT-015, FR-WEB-001, FR-API-001]
depends_on: [FR-PLAT-004]
blocks: [FR-PLAT-012, FR-PLAT-013, FR-PLAT-014, FR-PLAT-015]
new_paths:
  - docs/deploy/topology.md
  - docs/contracts/deploy-topology.md
---

## §1 - Description (BCP-14 normative)

This FR freezes the **production topology** for Tam Thuc Strategem, aligned with CyberOS multi-surface deploy practice and the operator preference:

| Surface | Platform | Artefact |
|---|---|---|
| User web | **Vercel** | Next.js `apps/web` (standalone/static export as required by Vercel) |
| Database | **Supabase** (hosted Postgres) | Forward-only SQL under `db/migrations/` + RLS (FR-PLAT-003) |
| Backend API (+ engine CLI/images) | **Custom VPS** | Docker Compose, GHCR images, Caddy TLS edge |

The monorepo SHALL remain the single source of truth. A push to `main` SHALL be able to advance all three surfaces without three divergent repos. Web SHALL never hold DB credentials that can bypass RLS for other tenants; the API on the VPS is the only writer of user-scoped data. The web SHALL call the public API origin over HTTPS (`NEXT_PUBLIC_API_BASE` / server `API_URL`). Secrets SHALL live only in Vercel env, Supabase dashboard, and VPS env files — never in git.

This FR owns the topology document and the cross-surface invariants. It does NOT implement migrate scripts (FR-PLAT-012), VPS compose (FR-PLAT-013), Vercel project config (FR-PLAT-014), or the CD workflow split (FR-PLAT-015).

## §2 - Why this design

CyberOS already separates **web surface** from **VPS services** and uses **Supabase as the Postgres of record** with migrations applied on deploy. Strategem mirrors that split with one explicit change preferred by the operator: the **user-facing Next app ships on Vercel** (fast CDN, preview deploys, zero Node host on the VPS), while **compute and secrets for cast/RAG stay on a VPS** the team controls. Supabase keeps FR-PLAT-003 RLS and VN PDPD/GDPR erasure paths on managed Postgres without operating the DB host.

## §3 - Contract

### Invariants

1. Web → API only over HTTPS public origin; no direct Supabase service-role key in the browser.
2. API → Supabase via `DATABASE_URL` (pooler URL preferred for serverless-adjacent patterns; session mode when RLS session vars require it).
3. Engines run as VPS-side processes/containers; web never shells to `cast-cli`.
4. Migrations are forward-only SQL checked into `db/migrations/`.
5. Rollback: Vercel redeploy previous deployment; VPS re-pull prior image tag; DB via new reverse migration (not auto-down).

### Env map (names only)

| Surface | Vars (examples) |
|---|---|
| Vercel | `NEXT_PUBLIC_API_BASE`, `API_URL` (SSR rewrite target if used) |
| VPS | `DATABASE_URL`, `JWT_SECRET`, `TAMTHUC_AUTH_*`, `CAST_CLI`, image tags |
| Supabase | project URL, anon key (optional for future client auth), service role (API only, VPS) |

## §4 - Acceptance criteria

1. `docs/deploy/topology.md` states the three-surface table and the five invariants.
2. No production path requires the VPS to serve the Next.js user UI.
3. No production path requires the browser to hold a Supabase service-role key.
4. Related FRs 012–015 depend on this document and cite it.

## §5 - Verification

- Doc review against cyberos `docs/deploy/*` and `deploy/vps/*` patterns.
- Grep: browser code has no `SERVICE_ROLE` / service-role env usage.

## §6 - Implementation skeleton

1. Author `docs/deploy/topology.md` + short contract pointer.
2. Cross-link from `deploy/README.md`.
