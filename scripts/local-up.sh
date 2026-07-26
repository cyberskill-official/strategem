#!/usr/bin/env bash
# Local Docker + LM Studio health matrix (Phase 4).
# Usage: from repo root — bash scripts/local-up.sh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
COMPOSE_FILE="${COMPOSE_FILE:-deploy/compose/docker-compose.local.yml}"
API_PORT="${LOCAL_API_PORT:-8000}"
WEB_PORT="${LOCAL_WEB_PORT:-3000}"
PG_PORT="${LOCAL_PG_PORT:-5432}"

cd "$ROOT"

export LOCAL_API_PORT="$API_PORT"
export LOCAL_WEB_PORT="$WEB_PORT"
export LOCAL_PG_PORT="$PG_PORT"
export NEXT_PUBLIC_API_BASE="${NEXT_PUBLIC_API_BASE:-http://127.0.0.1:${API_PORT}}"
export API_URL="${API_URL:-http://api:8000}"
export PAYMENTS_MODE="${PAYMENTS_MODE:-mock}"
export CORS_ORIGINS="${CORS_ORIGINS:-http://127.0.0.1:${WEB_PORT},http://localhost:${WEB_PORT},http://127.0.0.1:3000,http://localhost:3000}"
# Do not inherit host/prod LLM_* into compose; use LOCAL_LLM_* to override.
export LOCAL_LLM_BACKEND="${LOCAL_LLM_BACKEND:-openai_compatible}"
export LOCAL_LLM_BASE_URL="${LOCAL_LLM_BASE_URL:-http://host.docker.internal:1234/v1}"
export LOCAL_LLM_MODEL="${LOCAL_LLM_MODEL:-local-model}"
export LOCAL_LLM_API_KEY="${LOCAL_LLM_API_KEY:-}"
# Host-side probe uses loopback (not host.docker.internal).
LLM_BASE="${LOCAL_LLM_PROBE_URL:-http://127.0.0.1:1234/v1}"

echo "==> Starting compose stack (build if needed)"
docker compose -f "$COMPOSE_FILE" up --build -d

probe() {
  local name="$1" url="$2"
  if curl -fsS --max-time 5 "$url" >/dev/null 2>&1; then
    printf '  [ok]   %s  %s\n' "$name" "$url"
    return 0
  fi
  printf '  [FAIL] %s  %s\n' "$name" "$url"
  return 1
}

probe_json() {
  local name="$1" url="$2" expect="$3"
  local body
  if ! body="$(curl -fsS --max-time 8 "$url" 2>/dev/null)"; then
    printf '  [FAIL] %s  %s (unreachable)\n' "$name" "$url"
    return 1
  fi
  if printf '%s' "$body" | grep -q "$expect"; then
    printf '  [ok]   %s  %s\n' "$name" "$url"
    return 0
  fi
  printf '  [WARN] %s  %s  body=%s\n' "$name" "$url" "$(printf '%s' "$body" | head -c 200)"
  return 1
}

echo ""
echo "==> Health matrix"
fail=0
probe "postgres(host)" "http://127.0.0.1:${PG_PORT}" && true || {
  # pg_isready is better; fall back to docker compose ps
  if docker compose -f "$COMPOSE_FILE" ps postgres | grep -q "healthy\|running"; then
    printf '  [ok]   postgres  compose service healthy/running\n'
  else
    printf '  [FAIL] postgres  not healthy\n'
    fail=1
  fi
}

# Wait for API
for _ in $(seq 1 30); do
  if curl -fsS --max-time 2 "http://127.0.0.1:${API_PORT}/healthz" >/dev/null 2>&1; then
    break
  fi
  sleep 1
done

probe "api/healthz" "http://127.0.0.1:${API_PORT}/healthz" || fail=1
probe_json "api/ready" "http://127.0.0.1:${API_PORT}/ready" '"status"' || fail=1
probe "web" "http://127.0.0.1:${WEB_PORT}" || fail=1

# Host LM Studio (optional — degraded UX when down)
llm_host="${LLM_BASE%/v1}/v1/models"
llm_host="${LLM_BASE%/}/models"
# Normalize: if LLM_BASE ends with /v1 use it; else append
if [[ "$LLM_BASE" == */v1 ]]; then
  llm_models="${LLM_BASE}/models"
else
  llm_models="${LLM_BASE%/}/v1/models"
fi
if curl -fsS --max-time 3 "$llm_models" >/dev/null 2>&1; then
  printf '  [ok]   lmstudio  %s\n' "$llm_models"
else
  printf '  [WARN] lmstudio  %s (unreachable — API will degrade interpretation gracefully)\n' "$llm_models"
fi

echo ""
echo "Tips:"
echo "  - Set LLM_MODEL to the exact id from LM Studio Local Server UI."
echo "  - READY_REQUIRE_LLM=1 makes /ready fail when the LLM backend is unreachable."
echo "  - PAYMENTS_MODE=mock enables local PayOS-free premium upgrade tests."
echo "  - Tear down: docker compose -f $COMPOSE_FILE down -v"
echo ""

if [[ "$fail" -ne 0 ]]; then
  echo "Health matrix incomplete — inspect: docker compose -f $COMPOSE_FILE logs"
  exit 1
fi
echo "Local stack is up."
