"""Postgres-backed query store — COV-010 + W2 RLS domain tables.

When DATABASE_URL is set the cast path:
  1. Upserts a users row (anon well-known UUID or JWT subject)
  2. Writes PLAT-003 domain tables (queries / charts / reports / audit_logs)
  3. Keeps app_query_store as the full orchestrator JSON payload for GET-by-id

Session GUC ``app.current_user_id`` is set per transaction so app_user DSNs
honour fail-closed RLS (db/rls/session.md). Superuser local compose bypasses RLS
but still sets the GUC for correctness.
"""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, cast
from uuid import UUID, uuid4

import psycopg
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

# Fixed anonymous principal (db/migrations/0011_anon_user.sql).
ANON_USER_UUID = UUID("00000000-0000-4000-8000-0000000000a1")

_HE_MAP = {
    "qimen": "ky_mon",
    "ky_mon": "ky_mon",
    "liuren": "luc_nham",
    "luc_nham": "luc_nham",
    "taiyi": "thai_at",
    "thai_at": "thai_at",
}


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


def resolve_user_uuid(user_id: str | None) -> UUID:
    """Map anon / non-UUID subjects onto the well-known anonymous user."""
    raw = (user_id or "anon").strip()
    if not raw or raw.lower() in {"anon", "anonymous"}:
        return ANON_USER_UUID
    try:
        return UUID(raw)
    except ValueError:
        # Stable synthetic UUID for opaque string ids (tests / legacy).
        digest = hashlib.sha256(raw.encode()).hexdigest()
        return UUID(digest[:32])


def _system_to_he(system: str, envelope: dict[str, Any]) -> str:
    he = envelope.get("he")
    if isinstance(he, str) and he:
        return _HE_MAP.get(he, he)
    return _HE_MAP.get(system, system)


def _cache_key(envelope: dict[str, Any], he: str) -> str:
    if isinstance(envelope.get("cache_key"), str) and envelope["cache_key"]:
        return str(envelope["cache_key"])
    prov = envelope.get("provenance")
    if isinstance(prov, dict) and prov.get("cache_key"):
        return str(prov["cache_key"])
    blob = json.dumps({"he": he, "dau_vao": envelope.get("dau_vao")}, sort_keys=True)
    return hashlib.sha256(blob.encode()).hexdigest()[:32]


def _engine_version(envelope: dict[str, Any]) -> str:
    prov = envelope.get("provenance")
    if isinstance(prov, dict) and prov.get("engine_version"):
        return str(prov["engine_version"])
    return str(envelope.get("engine_version") or envelope.get("envelope_version") or "1")


@dataclass
class PgQueryStore:
    """Postgres store: app_query_store + RLS domain tables."""

    dsn: str
    write_domain: bool = True

    def _conn(self) -> Any:
        return psycopg.connect(self.dsn, row_factory=dict_row)

    def _set_rls(self, conn: Any, user_uuid: UUID) -> None:
        conn.execute(
            "SELECT set_config('app.current_user_id', %s, true)",
            (str(user_uuid),),
        )

    def _ensure_user(self, conn: Any, user_uuid: UUID, *, tier: str = "free") -> None:
        email = (
            "anon@strategem.local"
            if user_uuid == ANON_USER_UUID
            else f"{user_uuid}@users.strategem.local"
        )
        conn.execute(
            """
            INSERT INTO users (id, email, display_name, tier, locale)
            VALUES (%s, %s, %s, %s, 'vi')
            ON CONFLICT (id) DO NOTHING
            """,
            (
                str(user_uuid),
                email,
                "Anonymous cast" if user_uuid == ANON_USER_UUID else None,
                tier or "free",
            ),
        )

    def _write_domain(
        self,
        conn: Any,
        *,
        user_uuid: UUID,
        qid: str,
        req: dict[str, Any],
        systems: list[str],
        payload: dict[str, Any],
        report_id: str | None,
    ) -> None:
        raw_charts = payload.get("charts")
        charts: dict[str, Any] = raw_charts if isinstance(raw_charts, dict) else {}
        interpretation = payload.get("interpretation")
        if not isinstance(interpretation, dict):
            interpretation = {}
        ai_disclosure = payload.get("ai_disclosure")
        if not isinstance(ai_disclosure, dict):
            raw_report = payload.get("report")
            report = raw_report if isinstance(raw_report, dict) else {}
            ai_disclosure = report.get("ai_disclosure") if isinstance(report, dict) else {}
        if not isinstance(ai_disclosure, dict):
            ai_disclosure = {"is_ai_generated": True, "model": "unknown"}

        dt = str(req.get("datetime") or payload.get("datetime") or "1970-01-01T00:00:00")
        tz = str(req.get("tz") or "+07:00")
        kinh = req.get("kinh_do")
        if kinh is None:
            kinh = req.get("longitude")
        place = req.get("place")
        qtype = str(req.get("question_type") or req.get("loai_cau_hoi") or "unknown")
        persona = str(req.get("persona_level") or "beginner")
        flags = req.get("co_truong_phai")
        sys_list = systems or list(charts.keys()) or ["qimen"]

        conn.execute(
            """
            INSERT INTO queries (
              id, user_id, datetime, tz, kinh_do, place, question_type,
              systems, persona_level, co_truong_phai, created_at
            ) VALUES (
              %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
            ON CONFLICT (id) DO UPDATE SET
              question_type = EXCLUDED.question_type,
              systems = EXCLUDED.systems,
              co_truong_phai = EXCLUDED.co_truong_phai
            """,
            (
                qid,
                str(user_uuid),
                dt,
                tz,
                float(kinh) if kinh is not None else None,
                place,
                qtype,
                sys_list,
                persona,
                Jsonb(flags) if isinstance(flags, dict) else None,
                datetime.now(UTC),
            ),
        )

        # Replace charts for this query (save_result re-calls create with same id).
        conn.execute("DELETE FROM charts WHERE query_id = %s", (qid,))
        for system, envelope in charts.items():
            if not isinstance(envelope, dict):
                continue
            he = _system_to_he(str(system), envelope)
            cid = str(uuid4())
            conn.execute(
                """
                INSERT INTO charts (
                  id, query_id, user_id, he, envelope, cache_key, engine_version, created_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    cid,
                    qid,
                    str(user_uuid),
                    he,
                    Jsonb(envelope),
                    _cache_key(envelope, he),
                    _engine_version(envelope),
                    datetime.now(UTC),
                ),
            )

        if report_id or payload.get("report"):
            raw_rid = report_id or (payload.get("report") or {}).get("report_id")
            try:
                rid = str(UUID(str(raw_rid))) if raw_rid else str(uuid4())
            except (ValueError, TypeError):
                # Non-UUID report ids (tests / legacy) → stable derived UUID
                rid = str(UUID(hashlib.sha256(str(raw_rid).encode()).hexdigest()[:32]))
            review = "not_required"
            if isinstance(interpretation, dict) and interpretation.get("review_status"):
                review = str(interpretation["review_status"])
            conn.execute(
                """
                INSERT INTO reports (
                  id, query_id, user_id, interpretation, ai_disclosure,
                  review_status, pdf_url, created_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                  interpretation = EXCLUDED.interpretation,
                  ai_disclosure = EXCLUDED.ai_disclosure,
                  review_status = EXCLUDED.review_status
                """,
                (
                    rid,
                    qid,
                    str(user_uuid),
                    Jsonb(interpretation),
                    Jsonb(ai_disclosure),
                    review,
                    None,
                    datetime.now(UTC),
                ),
            )

        conn.execute(
            """
            INSERT INTO audit_logs (
              user_id, action, resource_type, resource_id, metadata, created_at
            )
            SELECT %s, %s, %s, %s, %s, %s
            WHERE NOT EXISTS (
              SELECT 1 FROM audit_logs
              WHERE resource_id = %s AND action = 'chart_cast'
            )
            """,
            (
                str(user_uuid),
                "chart_cast",
                "query",
                qid,
                Jsonb(
                    {
                        "systems": sys_list,
                        "report_id": report_id,
                    }
                ),
                datetime.now(UTC),
                qid,
            ),
        )

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
        report_id_s = str(report_id) if report_id else None
        user_uuid = resolve_user_uuid(user_id)

        with self._conn() as conn:
            self._set_rls(conn, user_uuid)
            if self.write_domain:
                try:
                    self._ensure_user(
                        conn,
                        user_uuid,
                        tier=str(req.get("tier") or "free"),
                    )
                    self._write_domain(
                        conn,
                        user_uuid=user_uuid,
                        qid=qid,
                        req=req,
                        systems=systems,
                        payload=stored,
                        report_id=report_id_s,
                    )
                except Exception:
                    # Domain tables may be absent on older DBs that only have
                    # app_query_store — still persist the full payload.
                    conn.rollback()
                    self._set_rls(conn, user_uuid)

            conn.execute(
                """
                INSERT INTO app_query_store (id, user_id, payload, systems, question_type, report_id, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                  payload = EXCLUDED.payload,
                  systems = EXCLUDED.systems,
                  question_type = EXCLUDED.question_type,
                  report_id = EXCLUDED.report_id,
                  user_id = EXCLUDED.user_id
                """,
                (
                    qid,
                    str(user_uuid) if user_id not in (None, "", "anon") else "anon",
                    Jsonb(stored),
                    systems,
                    req.get("question_type") or req.get("loai_cau_hoi") or "unknown",
                    report_id_s,
                    datetime.now(UTC),
                ),
            )
            conn.commit()
        return qid

    def get(self, query_id: str) -> dict[str, Any] | None:
        try:
            with self._conn() as conn:
                row = conn.execute(
                    "SELECT payload FROM app_query_store WHERE id = %s",
                    (query_id,),
                ).fetchone()
        except Exception as e:
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
        sql = (
            "SELECT id, user_id, systems, question_type, report_id, created_at, payload "
            "FROM app_query_store WHERE 1=1"
        )
        args: list[Any] = []
        if user_id is not None:
            uid = str(resolve_user_uuid(user_id))
            aliases = {uid, user_id}
            if user_id.lower() in {"anon", "anonymous"} or uid == str(ANON_USER_UUID):
                aliases.add("anon")
                aliases.add(str(ANON_USER_UUID))
            sql += " AND user_id = ANY(%s)"
            args.append(list(aliases))
        if question_type:
            sql += " AND question_type = %s"
            args.append(question_type)
        sql += " ORDER BY created_at DESC LIMIT %s"
        args.append(limit)
        he_map = {"qimen": "ky_mon", "liuren": "luc_nham", "taiyi": "thai_at"}
        out: list[dict[str, Any]] = []
        with self._conn() as conn:
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

    def get_report(self, report_id: str) -> dict[str, Any] | None:
        """Resolve by report_id column/payload, or by cast query id (store id)."""
        with self._conn() as conn:
            row = conn.execute(
                """
                SELECT payload FROM app_query_store
                WHERE report_id = %s
                ORDER BY created_at DESC LIMIT 1
                """,
                (report_id,),
            ).fetchone()
            if not row:
                row = conn.execute(
                    """
                    SELECT payload FROM app_query_store
                    WHERE payload->>'report_id' = %s
                    ORDER BY created_at DESC LIMIT 1
                    """,
                    (report_id,),
                ).fetchone()
            if not row:
                row = conn.execute(
                    """
                    SELECT payload FROM app_query_store
                    WHERE id = %s OR payload->>'query_id' = %s
                    ORDER BY created_at DESC LIMIT 1
                    """,
                    (report_id, report_id),
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
            out.setdefault("report_id", payload.get("report_id") or report_id)
            out.setdefault("query_id", payload.get("query_id") or report_id)
            return out
        return None

    def count_domain_rows(self, query_id: str) -> dict[str, int]:
        """Test helper: row counts in RLS domain tables for a query id."""
        with self._conn() as conn:
            q = conn.execute(
                "SELECT count(*) AS n FROM queries WHERE id = %s", (query_id,)
            ).fetchone()
            c = conn.execute(
                "SELECT count(*) AS n FROM charts WHERE query_id = %s", (query_id,)
            ).fetchone()
            r = conn.execute(
                "SELECT count(*) AS n FROM reports WHERE query_id = %s", (query_id,)
            ).fetchone()
            a = conn.execute(
                "SELECT count(*) AS n FROM audit_logs WHERE resource_id = %s", (query_id,)
            ).fetchone()
        return {
            "queries": int(cast(Any, q)["n"]) if q else 0,
            "charts": int(cast(Any, c)["n"]) if c else 0,
            "reports": int(cast(Any, r)["n"]) if r else 0,
            "audit_logs": int(cast(Any, a)["n"]) if a else 0,
        }
