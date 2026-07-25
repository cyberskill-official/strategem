# Staging deploy wiring (COV-020)

Product staging path: **Vercel web → VPS API → Supabase Postgres**, with local Docker as the developer twin (`docker-compose.local.yml`).

## 1. Compose files

| File | Role |
|------|------|
| `deploy/compose/docker-compose.local.yml` | Build-from-source local enterprise stack |
| `deploy/compose/docker-compose.staging.yml` | GHCR image staging bootstrap |

Staging compose **must** set:

```bash
READY_REQUIRE_CAST_CLI=1
CAST_CLI=/src/cast-cli   # or image path
DATABASE_URL=postgresql://...
NEXT_PUBLIC_API_BASE=https://api.<staging-host>
CORS / API allow origin = Vercel production + preview
```

## 2. Health / ready

```bash
curl -sS "$API_BASE/healthz"   # liveness
curl -sS "$API_BASE/ready"     # CAST_CLI present when READY_REQUIRE_CAST_CLI=1
```

## 3. CORS + web base

- Web: `NEXT_PUBLIC_API_BASE` points at the public API origin.
- API CORS allows that Vercel origin (see `docs/deploy/vps-api.md`).

## 4. Smoke (KM / LN / TA)

```bash
export API_BASE=https://api.<staging-host>
bash scripts/smoke-staging.sh
```

## 5. Secrets (never commit)

Use env / secret manager only. Checklist: `docs/deploy/SHIP_CHECKLIST.md`.

| Secret | Surface |
|--------|---------|
| `POSTGRES_PASSWORD` / `DATABASE_URL` | Supabase or VPS |
| `TAMTHUC_AUTH_JWT_SECRET` | API |
| `TAMTHUC_AUTH_MASTER_KEY_B64` | API birth encryption |
| PayOS keys (`PAYOS_CLIENT_ID` / `PAYOS_API_KEY` / `PAYOS_CHECKSUM_KEY`) | API + webhook when COV-026 enabled (Stripe retired) |

## 6. Related

- Local Docker + LMStudio: `docs/deploy/local-docker-lmstudio.md`
- Topology: `docs/deploy/topology.md`
