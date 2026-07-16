# Vercel web (TASK-PLAT-014)

## Project

- Root directory: monorepo root **or** `apps/web` (prefer monorepo + filter — see `apps/web/vercel.json`).
- Framework: Next.js.
- Install: `pnpm install` (frozen lockfile in CI).
- Build: `pnpm --filter web build`.

## Environment variables

| Name | Required | Notes |
|---|---|---|
| `NEXT_PUBLIC_API_BASE` | yes (prod) | e.g. `https://api.example.com` — **no trailing slash** |
| `API_URL` | optional | SSR/rewrite target; same as public API origin |

Do **not** set Supabase service role in Vercel.

## CORS

API on VPS must allow:

- production Vercel domain
- `*.vercel.app` previews if used

## Local

```bash
pnpm --filter web dev
# rewrites /api → http://127.0.0.1:8000 when NEXT_PUBLIC_API_BASE is empty
```
