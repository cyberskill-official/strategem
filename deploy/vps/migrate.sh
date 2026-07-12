#!/usr/bin/env bash
# Apply db/migrations/*.sql to DATABASE_URL (prefer Supabase direct URL).
# Idempotent ledger: public._strategem_schema_migrations
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
MIG_DIR="${ROOT}/db/migrations"
URL="${DATABASE_URL_MIGRATE:-${DATABASE_URL:-}}"

if [[ -z "${URL}" ]]; then
  echo "migrate.sh: DATABASE_URL or DATABASE_URL_MIGRATE required" >&2
  exit 2
fi

if ! command -v psql >/dev/null 2>&1; then
  echo "migrate.sh: psql not found (install postgresql-client)" >&2
  exit 2
fi

export PGPASSWORD="${PGPASSWORD:-}"
PSQL=(psql "$URL" -v ON_ERROR_STOP=1 -q)

echo "==> ensuring migrations ledger"
"${PSQL[@]}" <<'SQL'
CREATE TABLE IF NOT EXISTS public._strategem_schema_migrations (
  filename text PRIMARY KEY,
  applied_at timestamptz NOT NULL DEFAULT now()
);
SQL

shopt -s nullglob
files=("${MIG_DIR}"/*.sql)
if [[ ${#files[@]} -eq 0 ]]; then
  echo "migrate.sh: no files in ${MIG_DIR}" >&2
  exit 2
fi

for f in "${files[@]}"; do
  base="$(basename "$f")"
  applied="$("${PSQL[@]}" -tAc "SELECT 1 FROM public._strategem_schema_migrations WHERE filename = '${base}'" | tr -d '[:space:]')"
  if [[ "$applied" == "1" ]]; then
    echo "skip  ${base}"
    continue
  fi
  echo "apply ${base}"
  "${PSQL[@]}" -f "$f"
  "${PSQL[@]}" -c "INSERT INTO public._strategem_schema_migrations (filename) VALUES ('${base}');"
done

echo "==> migrations complete"
