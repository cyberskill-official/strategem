#!/usr/bin/env bash
# Apply db/migrations via the Python migrator (D-MIG-001).
# Checksum ledger + advisory lock + one transaction per file.
# Prefer DATABASE_URL_MIGRATE (privileged) over runtime DATABASE_URL.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
URL="${DATABASE_URL_MIGRATE:-${DATABASE_URL:-}}"

if [[ -z "${URL}" ]]; then
  echo "migrate.sh: DATABASE_URL or DATABASE_URL_MIGRATE required" >&2
  exit 2
fi

export DATABASE_URL_MIGRATE="$URL"
export DATABASE_URL="${DATABASE_URL:-$URL}"

cd "$ROOT"

pick_python() {
  if [[ -x "${ROOT}/.venv/bin/python" ]]; then
    echo "${ROOT}/.venv/bin/python"
    return
  fi
  if command -v python3 >/dev/null 2>&1; then
    command -v python3
    return
  fi
  echo "migrate.sh: python3 not found (install venv or python3)" >&2
  exit 2
}

PY="$(pick_python)"
echo "==> migrate via db_schema.migrate (checksum + advisory lock)"
exec "$PY" -m db_schema.migrate
