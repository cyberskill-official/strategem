# Deploy

## Target topology (TASK-PLAT-011)

| Surface | Platform | Docs |
|---|---|---|
| User web | **Vercel** | `docs/deploy/vercel-web.md` |
| Database | **Supabase** Postgres | `docs/deploy/supabase.md` |
| Backend API | **Custom VPS** | `docs/deploy/vps-api.md` |
| CD split | GHCR + SSH + Vercel Git | `docs/deploy/cd-split.md` |

Full diagram: `docs/deploy/topology.md`.

## Layout

| Path | Role |
|---|---|
| `docker/*.Dockerfile` | engine / api / web multi-stage images |
| `compose/docker-compose.staging.yml` | local/staging bootstrap (Postgres, Redis, api, web) |
| `vps/` | production API compose, Caddy, migrate + deploy scripts |
| `environments/*.md` | staging + production contracts |
| `.github/workflows/cd.yml` | legacy multi-image CD (Docker web optional) |
| `.github/workflows/deploy-vps.yml` | **API** → GHCR → VPS (TASK-PLAT-015) |
| `.github/workflows/security-scan.yml` | Trivy fs + gitleaks on PR |

## Local

Full stack (build from source) + LMStudio: **`docs/deploy/local-docker-lmstudio.md`** (COV-027/028).

```bash
# integration tests (needs DATABASE_URL)
export DATABASE_URL=postgresql://postgres:postgres@localhost:5432/strategem
just db-test

# local compose (api+web+postgres+redis, builds cast-cli into api)
export LOCAL_API_PORT=18000 LOCAL_WEB_PORT=13000 LOCAL_PG_PORT=15432
export NEXT_PUBLIC_API_BASE=http://127.0.0.1:18000
docker compose -f deploy/compose/docker-compose.local.yml up --build -d

# build images alone
docker build -f deploy/docker/api.Dockerfile -t strategem-api:local .
```

## Secrets

Never commit secrets. Pipeline reads from GitHub Actions secrets / Environments. See TASK-PLAT-007 for the control set.

## Production approval

Configure repo → Settings → Environments → `production` → Required reviewers. Without approval, `deploy-prod` does not run.
