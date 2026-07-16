---
id: TASK-PLAT-014
title: "Vercel web deploy - apps/web on Vercel with public API base URL, no server secrets beyond rewrites, preview deploys on PR optional"
module: PLAT
priority: MUST
status: done
phase: P3
slice: 1
lang: typescript/iac
effort_h: 6
owner: Stephen Cheng (Founder/CPO)
created: 2026-07-13
refs: [cyberos vercel.json, strategy 4.1]
related_frs: [TASK-PLAT-011, TASK-WEB-001, TASK-WEB-002, TASK-API-002]
depends_on: [TASK-PLAT-011]
blocks: []
new_paths:
  - apps/web/vercel.json
  - apps/web/.env.example
  - docs/deploy/vercel-web.md
---

## §1 - Description (BCP-14 normative)

This task ships the **user web** surface to **Vercel**. The Next.js app under `apps/web` SHALL build on Vercel. Runtime configuration SHALL include:

- `NEXT_PUBLIC_API_BASE` — browser origin for the VPS API (e.g. `https://api.example.com`), empty string only when same-origin reverse proxy is used.
- Optional server-only `API_URL` for SSR/rewrites to the API (never a Supabase service role).

The browser SHALL NOT embed Supabase service-role keys. CORS on the API (TASK-PLAT-013) SHALL allow the Vercel production and preview origins.

`vercel.json` SHALL set install/build rooted at the monorepo as needed (`pnpm --filter web build` or `cd apps/web`). Output remains Next default / standalone as compatible with Vercel.

## §2 - Why this design

Vercel optimizes the user-facing SPA/SSR path; CyberOS already uses Vercel for docs-style surfaces. Keeping the web off the VPS reduces Node load from the API host and gives PR preview URLs for design review.

## §3 - Contract

| Env | Where | Purpose |
|---|---|---|
| `NEXT_PUBLIC_API_BASE` | Vercel | Browser API calls |
| `API_URL` | Vercel (optional) | Server rewrite target |

Production web MUST call HTTPS API. Local dev continues to rewrite `/api` → `127.0.0.1:8000`.

## §4 - Acceptance criteria

1. `apps/web/vercel.json` present and documents monorepo build.
2. `.env.example` lists public API base without secrets.
3. `docs/deploy/vercel-web.md` has project link steps and env checklist.
4. Cast client works when `NEXT_PUBLIC_API_BASE` is the VPS API origin (no `/api` rewrite required in prod).

## §5 - Verification

- `pnpm --filter web build` still green.
- Grep: no `SERVICE_ROLE` in `apps/web`.
