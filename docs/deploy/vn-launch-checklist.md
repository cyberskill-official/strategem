# VN launch deployment checklist

Locked topology: **web → Vercel**, **Postgres → Supabase**, **API + cast-cli → VPS**.
Payment rail: **PayOS only**. AI credentials: **operator BYOK** (not end-user browser keys).

## 1. Supabase (DB)

- [ ] Create project; copy pooler `DATABASE_URL` for API runtime
- [ ] Prefer direct DB URL for migrations (`DATABASE_URL_MIGRATE`)
- [ ] Run `uv run python -m db_schema.migrate` (includes `0015_payment_fulfillments`, `0016_operator_llm_settings`)
- [ ] Confirm RLS still applies (`docs/deploy/supabase.md`)

## 2. VPS API + cast-cli

- [ ] Copy `deploy/vps/.env.example` → `.env` (never commit secrets)
- [ ] Set `TAMTHUC_AUTH_JWT_SECRET` + `TAMTHUC_AUTH_MASTER_KEY_B64` (non-dev values)
- [ ] Set PayOS: `PAYOS_CLIENT_ID`, `PAYOS_API_KEY`, `PAYOS_CHECKSUM_KEY`
- [ ] Set `CORS_ORIGINS` to exact Vercel origin(s) — **fail-closed**; never `*`
- [ ] Set `APP_ENV=production`, `CAST_CLI` path, `DATABASE_URL`
- [ ] Deploy per `docs/deploy/vps-api.md`; smoke `/healthz` + `/ready`
- [ ] Register PayOS webhook URL: `https://<api-host>/api/v1/payments/webhook`

## 3. Vercel web

- [ ] `NEXT_PUBLIC_API_BASE=https://<api-host>`
- [ ] Server `API_URL` same API base (route handlers / rewrites)
- [ ] Deploy per `docs/deploy/vercel-web.md`
- [ ] Confirm browser CORS: login + cast from Vercel origin succeeds

## 4. Operator BYOK (optional free models / LM Studio)

- [ ] Promote an operator user to `tier=admin` in auth store
- [ ] `PUT /api/v1/operator/llm-settings` with OpenAI-compatible base URL + model
- [ ] Confirm response masks `api_key` (never returns raw key)
- [ ] Resolution order: operator settings → env (`LLM_*`) → stub
- [ ] Examples: LM Studio `http://host:1234/v1`, Groq/OpenRouter OpenAI-compatible endpoints

## 5. Local Docker + LM Studio (dev)

```bash
just local-up
# or: bash scripts/local-up.sh
```

Acceptance: migrations applied; `/ready` green with cast-cli; LM Studio optional with explicit degraded UI when down; `PAYMENTS_MODE=mock` checkout upgrades tier.

See `docs/deploy/local-docker-lmstudio.md`.
