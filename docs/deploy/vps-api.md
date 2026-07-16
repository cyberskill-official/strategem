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

## Rollback

Retag / set `API_IMAGE_TAG` to a previous git SHA and re-run `deploy.sh`.
