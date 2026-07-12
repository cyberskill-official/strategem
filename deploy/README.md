# Deploy (FR-PLAT-004)

## Layout

| Path | Role |
|---|---|
| `docker/*.Dockerfile` | engine / api / web multi-stage images |
| `compose/docker-compose.staging.yml` | staging bootstrap (Postgres, Redis, api, web) |
| `environments/*.md` | staging + production contracts |
| `.github/workflows/cd.yml` | integration → build → scan → staging → **approval** → prod |
| `.github/workflows/security-scan.yml` | Trivy fs + gitleaks on PR |

## Local

```bash
# integration tests (needs DATABASE_URL)
export DATABASE_URL=postgresql://postgres:postgres@localhost:5432/strategem
just db-test

# build images
docker build -f deploy/docker/api.Dockerfile -t strategem-api:local .
```

## Secrets

Never commit secrets. Pipeline reads from GitHub Actions secrets / Environments.
See FR-PLAT-007 for the control set.

## Production approval

Configure repo → Settings → Environments → `production` → Required reviewers.
Without approval, `deploy-prod` does not run.
