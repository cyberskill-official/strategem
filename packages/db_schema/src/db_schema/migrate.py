"""Apply db/migrations/*.sql with checksum ledger + advisory lock (D-MIG-001).

Aligns with deploy/vps/migrate.sh: one Python migrator for CI and production.
SQL apply and ledger insert share one transaction per file. Concurrent runners
are serialized via pg_advisory_lock. Checksum drift fails closed (dirty state).
"""

from __future__ import annotations

import hashlib
import logging
import os
import sys
import time
from pathlib import Path
from typing import Any

import psycopg

from db_schema import list_migrations

log = logging.getLogger("db_schema.migrate")

# Stable 64-bit key for pg_advisory_lock (namespace "strategem.migrations").
_ADVISORY_LOCK_KEY = 0x53545247_4D494731  # "STRG" + "MIG1"

_TOOL_VERSION = "db_schema.migrate/2"

_LEDGER_DDL = """
CREATE TABLE IF NOT EXISTS public._strategem_schema_migrations (
  filename text PRIMARY KEY,
  applied_at timestamptz NOT NULL DEFAULT now(),
  checksum text,
  status text NOT NULL DEFAULT 'applied',
  duration_ms integer,
  tool_version text
);
ALTER TABLE public._strategem_schema_migrations
  ADD COLUMN IF NOT EXISTS checksum text;
ALTER TABLE public._strategem_schema_migrations
  ADD COLUMN IF NOT EXISTS status text NOT NULL DEFAULT 'applied';
ALTER TABLE public._strategem_schema_migrations
  ADD COLUMN IF NOT EXISTS duration_ms integer;
ALTER TABLE public._strategem_schema_migrations
  ADD COLUMN IF NOT EXISTS tool_version text;
"""


class MigrationDirtyError(RuntimeError):
    """Ledger checksum does not match the on-disk migration file."""


def file_checksum(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def ensure_ledger(conn: psycopg.Connection[Any]) -> None:
    conn.execute(_LEDGER_DDL)


def _acquire_lock(conn: psycopg.Connection[Any]) -> None:
    conn.execute("SELECT pg_advisory_lock(%s)", (_ADVISORY_LOCK_KEY,))
    log.info("migrate.lock_acquired", extra={"key": _ADVISORY_LOCK_KEY})


def _release_lock(conn: psycopg.Connection[Any]) -> None:
    conn.execute("SELECT pg_advisory_unlock(%s)", (_ADVISORY_LOCK_KEY,))
    log.info("migrate.lock_released", extra={"key": _ADVISORY_LOCK_KEY})


def apply_migrations(dsn: str, *, migrations: list[Path] | None = None) -> int:
    """Apply pending migration files in order. Returns count newly applied.

    Raises MigrationDirtyError when an already-applied file's checksum differs.
    """
    files = migrations if migrations is not None else list_migrations()
    log.info("migrate.start", extra={"count": len(files), "dsn_host": _redact_dsn(dsn)})
    applied = 0
    with psycopg.connect(dsn) as conn:
        ensure_ledger(conn)
        conn.commit()
        _acquire_lock(conn)
        conn.commit()
        try:
            for path in files:
                checksum = file_checksum(path)
                row = conn.execute(
                    "SELECT checksum, status FROM public._strategem_schema_migrations "
                    "WHERE filename = %s",
                    (path.name,),
                ).fetchone()
                if row is not None:
                    stored = row[0]
                    status = row[1] if len(row) > 1 else "applied"
                    if status == "dirty":
                        raise MigrationDirtyError(
                            f"migration {path.name} marked dirty; refuse to continue"
                        )
                    if stored and stored != checksum:
                        conn.execute(
                            "UPDATE public._strategem_schema_migrations "
                            "SET status = 'dirty' WHERE filename = %s",
                            (path.name,),
                        )
                        conn.commit()
                        raise MigrationDirtyError(
                            f"checksum mismatch for {path.name}: ledger={stored} disk={checksum}"
                        )
                    if not stored:
                        # Backfill checksum for pre-D-MIG-001 ledger rows.
                        conn.execute(
                            "UPDATE public._strategem_schema_migrations "
                            "SET checksum = %s, tool_version = COALESCE(tool_version, %s) "
                            "WHERE filename = %s",
                            (checksum, _TOOL_VERSION, path.name),
                        )
                        conn.commit()
                    log.info("migrate.skip", extra={"file": path.name})
                    continue
                sql = path.read_text(encoding="utf-8")
                log.info("migrate.apply", extra={"file": path.name, "checksum": checksum})
                started = time.perf_counter()
                with conn.transaction():
                    # Multi-statement scripts: same path as prior migrator.
                    conn.execute(sql)
                    duration_ms = int((time.perf_counter() - started) * 1000)
                    conn.execute(
                        "INSERT INTO public._strategem_schema_migrations "
                        "(filename, checksum, status, duration_ms, tool_version) "
                        "VALUES (%s, %s, 'applied', %s, %s)",
                        (path.name, checksum, duration_ms, _TOOL_VERSION),
                    )
                applied += 1
        finally:
            try:
                _release_lock(conn)
                conn.commit()
            except Exception:
                log.exception("migrate.lock_release_failed")
    log.info("migrate.complete", extra={"applied": applied})
    return applied


def _redact_dsn(dsn: str) -> str:
    # Never log password; keep host/db for ops.
    if "@" in dsn:
        return "postgresql://***@" + dsn.split("@", 1)[1]
    return "postgresql://***"


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s %(message)s")
    dsn = os.environ.get("DATABASE_URL_MIGRATE") or os.environ.get("DATABASE_URL")
    if not dsn:
        print("DATABASE_URL or DATABASE_URL_MIGRATE is required", file=sys.stderr)
        return 2
    try:
        n = apply_migrations(dsn)
    except MigrationDirtyError as e:
        print(f"migrate dirty: {e}", file=sys.stderr)
        return 3
    print(f"applied {n} migrations")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
