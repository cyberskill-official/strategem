"""Postgres-backed query store — COV-010 (DATABASE_URL path) + TT-008 RLS GUC."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, cast
from uuid import uuid4

import psycopg
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb


def database_url() -> str | None:
    return os.environ.get("DATABASE_URL") or None


def require_database_or_memory() -> str:
    """Return backend mode: 'postgres' | 'memory'. Fail closed in production."""
    if database_url():
        return "postgres"
    app_env = (os.environ.get("APP_ENV") or os.environ.get("ENV") or "").lower()
    allow_mem = os.environ.get("ALLOW_MEMORY_PERSISTENCE", "").strip().lower() in {
        "1",
        "true",
        "yes",
    }
    if app_env in {"production", "prod"} and not allow_mem:
        raise RuntimeError(
            "DATABASE_URL is required when APP_ENV=production "
            "(set ALLOW_MEMORY_PERSISTENCE=1 only for explicit break-glass)"
        )
    return "memory"


def set_rls_guc(conn: Any, user_id: str | None, *, role: str | None = None) -> None:
    """SET LOCAL app.current_user_id (and optional app.current_role) for RLS."""
    uid = user_id if user_id is not None else ""
    conn.execute("SELECT set_config('app.current_user_id', %s, true)", (uid,))
    if role is not None:
        conn.execute("SELECT set_config('app.current_role', %s, true)", (role,))


@dataclass
class PgQueryStore:
    """Single-table store for full cast results (query + charts + report)."""

    dsn: str

    def _conn(self) -> Any:
        # dict_row → dict[str, Any] rows; cast avoids psycopg generic mismatch under mypy
        return psycopg.connect(self.dsn, row_factory=dict_row)

    def create(
        self,
        user_id: str,
        req: dict[str, Any],
        systems: list[str],
        payload: dict[str, Any],
        *,
        query_id: str | None = None,
    ) -> str:
        qid = query_id or str(uuid4())
        stored = dict(payload)
        stored["query_id"] = qid
        report_id = stored.get("report_id")
        if isinstance(report_id, dict):
            report_id = report_id.get("report_id")
        uid = user_id or "anon"
        with self._conn() as conn:
            set_rls_guc(conn, uid)
            conn.execute(
                """
                INSERT INTO app_query_store (id, user_id, payload, systems, question_type, report_id, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                  payload = EXCLUDED.payload,
                  systems = EXCLUDED.systems,
                  question_type = EXCLUDED.question_type,
                  report_id = EXCLUDED.report_id
                """,
                (
                    qid,
                    uid,
                    Jsonb(stored),
                    systems,
                    req.get("question_type") or req.get("loai_cau_hoi") or "unknown",
                    str(report_id) if report_id else None,
                    datetime.now(UTC),
                ),
            )
            conn.commit()
        return qid

    def get(self, query_id: str, *, user_id: str | None = None) -> dict[str, Any] | None:
        try:
            with self._conn() as conn:
                if user_id is not None:
                    set_rls_guc(conn, user_id)
                row = conn.execute(
                    "SELECT payload FROM app_query_store WHERE id = %s",
                    (query_id,),
                ).fetchone()
        except Exception as e:
            # Invalid UUID / bad id → treat as miss (404 at route), not 500
            msg = str(e).lower()
            if "uuid" in msg or "invalid input" in msg or "syntax" in msg:
                return None
            raise
        if not row:
            return None
        payload = cast(Any, row)["payload"]
        if isinstance(payload, str):
            return cast(dict[str, Any], json.loads(payload))
        return dict(payload) if isinstance(payload, dict) else None

    def list_queries(
        self,
        *,
        user_id: str | None = None,
        he: str | None = None,
        question_type: str | None = None,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        sql = "SELECT id, user_id, systems, question_type, report_id, created_at, payload FROM app_query_store WHERE 1=1"
        args: list[Any] = []
        if user_id is not None:
            sql += " AND user_id = %s"
            args.append(user_id)
        if question_type:
            sql += " AND question_type = %s"
            args.append(question_type)
        sql += " ORDER BY created_at DESC LIMIT %s"
        args.append(limit)
        he_map = {"qimen": "ky_mon", "liuren": "luc_nham", "taiyi": "thai_at"}
        out: list[dict[str, Any]] = []
        with self._conn() as conn:
            if user_id is not None:
                set_rls_guc(conn, user_id)
            rows = conn.execute(sql, args).fetchall()
        for raw in rows:
            r = cast(dict[str, Any], raw)
            systems = list(r.get("systems") or [])
            he_val = systems[0] if systems else ""
            he_label = he_map.get(str(he_val), str(he_val))
            if he and he not in (he_val, he_label) and he not in systems:
                continue
            created = r.get("created_at")
            if created is not None and hasattr(created, "isoformat"):
                created_s = created.isoformat()
            else:
                created_s = str(created or "")
            out.append(
                {
                    "query_id": str(r["id"]),
                    "he": he_label or he_val,
                    "question_type": r.get("question_type") or "unknown",
                    "created_at": created_s,
                    "report_id": r.get("report_id"),
                    "user_id": r.get("user_id"),
                }
            )
        return out

    def get_report(self, report_id: str, *, user_id: str | None = None) -> dict[str, Any] | None:
        with self._conn() as conn:
            if user_id is not None:
                set_rls_guc(conn, user_id)
            row = conn.execute(
                """
                SELECT id, report_id, payload FROM app_query_store
                WHERE report_id = %s
                   OR id::text = %s
                   OR payload->>'report_id' = %s
                ORDER BY created_at DESC LIMIT 1
                """,
                (report_id, report_id, report_id),
            ).fetchone()
        if not row:
            return None
        payload = cast(Any, row)["payload"]
        if isinstance(payload, str):
            payload = json.loads(payload)
        if not isinstance(payload, dict):
            return None
        report = payload.get("report")
        if isinstance(report, dict):
            out = dict(report)
            out.setdefault("report_id", payload.get("report_id") or row.get("report_id"))
            out.setdefault("query_id", payload.get("query_id") or str(row["id"]))
            return out
        return None
