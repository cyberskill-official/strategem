# Deploy topology (FR-PLAT-011)

Aligned with CyberOS multi-surface deploy (`docs/deploy/*`, `deploy/vps/*`) and the operator preference for Strategem:

| Surface | Platform | What runs |
|---|---|---|
| **User web** | [Vercel](https://vercel.com) | Next.js `apps/web` |
| **Database** | [Supabase](https://supabase.com) Postgres | `db/migrations/*` + RLS (FR-PLAT-003) |
| **Backend API** | Custom **VPS** | `tamthuc-api` container, `cast-cli`, Caddy TLS |

```
  Browser ──HTTPS──► Vercel (web)
                │
                │ NEXT_PUBLIC_API_BASE
                ▼
            VPS Caddy ──► tamthuc-api ──DATABASE_URL──► Supabase Postgres
                              │
                              └── cast-cli / engines
```

## Invariants

1. **Browser never holds** Supabase service-role keys or master encryption keys.
2. **API is the only writer** of user-scoped rows; RLS remains fail-closed.
3. **VPS does not host** the user Next.js UI (web is Vercel-only in production).
4. **Migrations are forward-only** SQL in-repo; applied before API roll (`migrate.sh`).
5. **Secrets** live in Vercel env, Supabase dashboard, and VPS `.env` only — never git.

## Related

- FR-PLAT-012 Supabase migrate path → `docs/deploy/supabase.md`
- FR-PLAT-013 VPS API → `docs/deploy/vps-api.md`
- FR-PLAT-014 Vercel web → `docs/deploy/vercel-web.md`
- FR-PLAT-015 CD split → `docs/deploy/cd-split.md`
