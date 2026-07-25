"""Apply db/migrations/*.sql in lexicographic order with a schema ledger.

Aligns with deploy/vps/migrate.sh (`public._strategem_schema_migrations`):
skip already-applied files; one transaction per file (SQL + ledger insert).
"""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path
from typing import Any

import psycopg

from db_schema import list_migrations

log = logging.getLogger("db_schema.migrate")

_LEDGER_DDL = """
CREATE TABLE IF NOT EXISTS public._strategem_schema_migrations (
  filename text PRIMARY KEY,
  applied_at timestamptz NOT NULL DEFAULT now()
);
"""


def ensure_ledger(conn: psycopg.Connection[Any]) -> None:
    conn.execute(_LEDGER_DDL)


def apply_migrations(dsn: str, *, migrations: list[Path] | None = None) -> int:
    """Apply pending migration files in order. Returns count newly applied."""
    files = migrations if migrations is not None else list_migrations()
    log.info("migrate.start", extra={"count": len(files), "dsn_host": _redact_dsn(dsn)})
    applied = 0
    with psycopg.connect(dsn) as conn:
        ensure_ledger(conn)
        conn.commit()
        for path in files:
            row = conn.execute(
                "SELECT 1 FROM public._strategem_schema_migrations WHERE filename = %s",
                (path.name,),
            ).fetchone()
            if row is not None:
                log.info("migrate.skip", extra={"file": path.name})
                continue
            sql = path.read_text(encoding="utf-8")
            log.info("migrate.apply", extra={"file": path.name})
            with conn.transaction():
                # Multi-statement scripts: same path as prior migrator (libpq simple query).
                conn.execute(sql)
                conn.execute(
                    "INSERT INTO public._strategem_schema_migrations (filename) VALUES (%s)",
                    (path.name,),
                )
            applied += 1
    log.info("migrate.complete", extra={"applied": applied})
    return applied


def _redact_dsn(dsn: str) -> str:
    # Never log password; keep host/db for ops.
    if "@" in dsn:
        return "postgresql://***@" + dsn.split("@", 1)[1]
    return "postgresql://***"


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s %(message)s")
    dsn = os.environ.get("DATABASE_URL")
    if not dsn:
        print("DATABASE_URL is required", file=sys.stderr)
        return 2
    n = apply_migrations(dsn)
    print(f"applied {n} migrations")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
