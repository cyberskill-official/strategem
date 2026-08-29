# VPS API runtime (TASK-PLAT-013)

Pattern mirrors CyberOS `deploy/vps/deploy.sh`: **CI builds images → GHCR → VPS pulls**.

## One-time bootstrap

1. VPS with Docker Compose v2 + DNS `A` record for `api.<your-domain>`.
2. Clone repo (deploy key) to e.g. `~/strategem`.
3. `cp deploy/vps/.env.example deploy/vps/.env` and fill secrets.
4. GHCR login if packages are private.
5. First: `bash deploy/vps/migrate.sh` then `bash deploy/vps/deploy.sh`.

## Layout

| File | Role |
|---|---|
| `docker-compose.api.yml` | `api` + `caddy` |
| `Caddyfile` | TLS + reverse proxy → api:8000 |
| `deploy.sh` | pull + migrate + up |
| `migrate.sh` | apply `db/migrations` |
| `.env.example` | secret names |

## Health

```bash
curl -fsS https://api.<domain>/healthz
```

## Image pin (D-CD-001 / D-IMAGE-001)

CI (`deploy-vps.yml`) writes `API_IMAGE` as an **immutable digest** reference:

```text
ghcr.io/cyberskill-official/strategem-api@sha256:<digest>
```

Do not point production at floating `:main`. The `:main` GHCR tag may exist as a convenience pointer only.

Production SSH rolls wait on GitHub Environment **`production`** required reviewers — see `docs/deploy/branch-protection-main.md`.

## Rollback

Set `API_IMAGE` in `deploy/vps/.env` to a **previous known-good digest** (from the prior Actions run summary or `docker inspect`) and re-run `deploy.sh`. Prefer digest over a mutable tag.
