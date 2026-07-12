---
id: FR-PLAT-013
title: "VPS API runtime - Docker Compose for tamthuc-api (+ cast-cli image), Caddy TLS reverse proxy, deploy.sh roll script, env template; VPS never builds Rust if images are pre-built"
module: PLAT
priority: MUST
status: done
phase: P3
slice: 1
lang: iac
effort_h: 10
owner: Stephen Cheng (Founder/CPO)
created: 2026-07-13
refs: [cyberos deploy/vps/deploy.sh, cyberos deploy/vps/auto-deploy.md]
related_frs: [FR-PLAT-004, FR-PLAT-011, FR-PLAT-012, FR-PLAT-015, FR-API-001]
depends_on: [FR-PLAT-011, FR-PLAT-012]
blocks: [FR-PLAT-015]
new_paths:
  - deploy/vps/docker-compose.api.yml
  - deploy/vps/Caddyfile
  - deploy/vps/deploy.sh
  - deploy/vps/.env.example
  - deploy/vps/README.md
  - docs/deploy/vps-api.md
---

## §1 - Description (BCP-14 normative)

This FR defines the **custom VPS** runtime for the Strategem backend: the Python API (`tamthuc-api`), optional engine/cast-cli sidecar or baked binary, and Caddy as the public HTTPS edge for `api.<domain>`. Following CyberOS VPS practice:

- Images are built on CI and pushed to a registry (GHCR); the VPS **pulls and restarts**, it does not `cargo build` on a small box.
- `deploy/vps/deploy.sh` is the single roll entry (manual or SSH from Actions).
- Config is `.env` on the host (from `.env.example`); never committed with secrets.
- On roll: `git pull` (compose/Caddyfile) → `migrate.sh` → `docker compose pull` → `up -d`.

The VPS SHALL NOT be required to host the Next.js user UI (that is Vercel, FR-PLAT-014).

## §2 - Why this design

CyberOS proved that small VPS boxes die under release builds; GHCR + pull keeps deploys fast. Caddy gives automatic TLS. Compose keeps the stack readable. Separating API host from Vercel web matches the operator preference and reduces origin concerns (CORS / public API base URL).

## §3 - Contract

### Services (compose)

| Service | Image | Port (internal) |
|---|---|---|
| api | `ghcr.io/<org>/strategem-api:<tag>` | 8000 |
| caddy | caddy:2 | 80/443 |

`CAST_CLI` path inside the api image or a volume-mounted binary. `DATABASE_URL` points at Supabase.

### deploy.sh

```text
git pull --ff-only
bash deploy/vps/migrate.sh
docker compose -f deploy/vps/docker-compose.api.yml --env-file .env pull
docker compose ... up -d
healthcheck: curl -fsS https://api.<domain>/healthz || curl localhost:8000/healthz
```

## §4 - Acceptance criteria

1. Compose file and Caddyfile exist and reference env substitution.
2. `.env.example` lists every required secret name without values.
3. `deploy.sh` is idempotent and fails closed on migrate failure.
4. README documents one-time VPS bootstrap (Docker, deploy key, GHCR login, DNS).

## §5 - Verification

- `docker compose config` validates (when Docker available).
- Doc review against cyberos `deploy/vps/deploy.sh` structure.
