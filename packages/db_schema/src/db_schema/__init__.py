"""TASK-PLAT-003: ordered SQL migration apply + schema helpers."""

from __future__ import annotations

__all__ = ["migrations_dir", "list_migrations"]

from pathlib import Path


def migrations_dir() -> Path:
    """Resolve repo `db/migrations/` relative to this package or CWD."""
    here = Path(__file__).resolve()
    # packages/db_schema/src/db_schema/__init__.py → repo root
    candidates = [
        here.parents[4] / "db" / "migrations",  # .../strategem/db/migrations
        Path.cwd() / "db" / "migrations",
    ]
    for c in candidates:
        if c.is_dir():
            return c
    raise FileNotFoundError("db/migrations not found; run from repo root")


def list_migrations() -> list[Path]:
    d = migrations_dir()
    files = sorted(d.glob("*.sql"))
    if not files:
        raise FileNotFoundError(f"no *.sql under {d}")
    return files
