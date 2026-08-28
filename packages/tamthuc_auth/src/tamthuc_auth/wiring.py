"""Auth backend wiring — TT-024.

- `ENV=test`: in-memory by default (unit tests). Set `AUTH_USE_POSTGRES=1` +
  `DATABASE_URL` for durable-auth integration tests.
- `ENV=development|dev` with `DATABASE_URL`: Postgres UserStore + revocation.
- Production/staging without `DATABASE_URL`: fail closed (unless
  `ALLOW_MEMORY_AUTH=1` break-glass).

In-memory is never the silent default in production.
"""

from __future__ import annotations

import logging
import os

from tamthuc_auth.config import is_dev_or_test_env
from tamthuc_auth.pg_store import PostgresUserStore, database_url
from tamthuc_auth.revocation import PostgresRevocationStore
from tamthuc_auth.service import AuthService
from tamthuc_auth.store import InMemoryUserStore
from tamthuc_auth.tokens import RevocationStore, TokenService, get_revocation_store

log = logging.getLogger("tamthuc_auth.wiring")


def require_auth_backend() -> str:
    """Return 'postgres' | 'memory'. Fail closed in production without DATABASE_URL."""
    dsn = database_url()
    env = (os.environ.get("ENV") or os.environ.get("APP_ENV") or "").strip().lower()
    force_pg = os.environ.get("AUTH_USE_POSTGRES", "").strip().lower() in {
        "1",
        "true",
        "yes",
    }
    allow_mem = os.environ.get("ALLOW_MEMORY_AUTH", "").strip().lower() in {
        "1",
        "true",
        "yes",
    }

    # Unit tests: keep auth in-memory unless explicitly opted in.
    if env == "test" and not force_pg:
        return "memory"

    if dsn:
        return "postgres"

    if env in {"development", "dev"} or allow_mem:
        return "memory"

    if env in {"production", "prod", "staging"}:
        raise RuntimeError(
            "DATABASE_URL is required for durable auth when APP_ENV/ENV is "
            f"{env!r} (set ALLOW_MEMORY_AUTH=1 only for explicit break-glass)"
        )

    if not env:
        # Empty ENV: local/unit convenience (same as historical AuthService()).
        return "memory"

    if is_dev_or_test_env():
        return "memory"

    raise RuntimeError(
        "DATABASE_URL is required for durable auth "
        "(set ENV=development for in-memory, or ALLOW_MEMORY_AUTH=1 to break-glass)"
    )


def build_auth_service() -> AuthService:
    """Construct AuthService with durable stores when backend is postgres."""
    mode = require_auth_backend()
    if mode == "postgres":
        dsn = database_url()
        assert dsn
        # D-DB-001: refuse superuser / BYPASSRLS (RLS would not bind).
        from db_schema.runtime_role import assert_unprivileged_runtime_role

        assert_unprivileged_runtime_role(dsn)
        store = PostgresUserStore(dsn)
        rev = PostgresRevocationStore(dsn)
        tokens = TokenService(store=rev)
        log.info("auth.backend", extra={"backend": "postgres"})
        return AuthService(store=store, tokens=tokens, revocation=rev)
    log.info("auth.backend", extra={"backend": "memory"})
    return AuthService(
        store=InMemoryUserStore(),
        tokens=TokenService(store=get_revocation_store()),
        revocation=get_revocation_store(),
    )


__all__ = [
    "RevocationStore",
    "build_auth_service",
    "require_auth_backend",
]
