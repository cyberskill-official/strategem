#!/usr/bin/env bash
# Roll Strategem API on the VPS (TASK-PLAT-013 / TASK-PLAT-015).
# CyberOS pattern: git pull → migrate → pull images → up -d
# Note: this script git-pulls, so changes to deploy.sh apply on the *next* deploy.
set -euo pipefail

REPO_DIR="${STRATEGEM_REPO_DIR:-$HOME/strategem}"
cd "$REPO_DIR"

echo "==> pulling latest main"
git pull --ff-only origin main

cd deploy/vps
if [[ ! -f .env ]]; then
  echo "deploy.sh: missing deploy/vps/.env (copy from .env.example)" >&2
  exit 2
fi

# shellcheck disable=SC1091
set -a
# shellcheck source=/dev/null
source .env
set +a

echo "==> migrations"
bash ./migrate.sh

COMPOSE=(docker compose --env-file .env -f docker-compose.api.yml)

echo "==> pull images"
"${COMPOSE[@]}" pull api || {
  echo "pull failed — building local image fallback is not enabled on VPS; fix GHCR access" >&2
  exit 1
}

echo "==> up"
"${COMPOSE[@]}" up -d

echo "==> health"
sleep 2
if curl -fsS "http://127.0.0.1:8000/healthz" >/dev/null 2>&1; then
  echo "healthz ok (local)"
else
  echo "warn: local healthz failed; check docker logs" >&2
fi

echo "==> deploy complete"
