"""TASK-PLAT-003 acceptance: migration apply, fail-closed RLS, isolation, GIN, admin.

Requires DATABASE_URL (CI service Postgres). Unit inventory tests always run.
"""

from __future__ import annotations

import json
import uuid
from typing import Any

import psycopg
import pytest

# Fixed principals for isolation proofs
USER_A = uuid.UUID("aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa")
USER_B = uuid.UUID("bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb")


def _ensure_app_roles(super_dsn: str) -> tuple[str, str]:
    """Return DSNs for migration LOGIN roles (0017 creates strategem_app).

    Also ensures strategem_admin for admin-bypass proofs (test-only LOGIN).
    """
    with psycopg.connect(super_dsn, autocommit=True) as conn:
        # 0017 creates strategem_app; assert attributes (D-DB-001).
        row = conn.execute(
            """
            SELECT rolsuper, rolbypassrls, rolcreatedb, rolcanlogin
            FROM pg_roles WHERE rolname = 'strategem_app'
            """
        ).fetchone()
        assert row is not None, "migration 0017 must create strategem_app"
        assert row[0] is False and row[1] is False and row[2] is False and row[3] is True

        conn.execute(
            """
            DO $$
            BEGIN
              IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'strategem_admin') THEN
                CREATE ROLE strategem_admin LOGIN PASSWORD 'strategem_admin'
                  NOSUPERUSER NOBYPASSRLS NOCREATEDB;
              END IF;
            END $$;
            """
        )
        conn.execute("GRANT app_user TO strategem_app")
        conn.execute("GRANT app_admin TO strategem_admin")
        conn.execute("GRANT USAGE ON SCHEMA public TO strategem_app, strategem_admin")

    def rewrite(user: str, password: str) -> str:
        # postgresql://user:pass@host:port/db
        if "://" not in super_dsn:
            raise ValueError("expected URL-style DATABASE_URL")
        scheme, rest = super_dsn.split("://", 1)
        if "@" in rest:
            rest = rest.split("@", 1)[1]
        return f"{scheme}://{user}:{password}@{rest}"

    return rewrite("strategem_app", "strategem_app"), rewrite("strategem_admin", "strategem_admin")


def _seed_as_super(super_dsn: str) -> None:
    """Insert two users and one chart/query/report each, bypassing RLS as superuser."""
    env_a = {
        "envelope_version": 1,
        "he": "ky_mon",
        "dau_vao": {"datetime": "2024-01-01T00:00:00", "tz": "+07:00", "kinh_do": 106.7},
    }
    env_b = {**env_a, "he": "luc_nham"}
    with psycopg.connect(super_dsn, autocommit=True) as conn:
        conn.execute("DELETE FROM reports")
        conn.execute("DELETE FROM charts")
        conn.execute("DELETE FROM queries")
        conn.execute("DELETE FROM audit_logs")
        conn.execute("DELETE FROM users")
        conn.execute(
            """
            INSERT INTO users (id, email, display_name)
            VALUES (%s, 'a@example.com', 'A'), (%s, 'b@example.com', 'B')
            """,
            (USER_A, USER_B),
        )
        conn.execute(
            """
            INSERT INTO queries (id, user_id, datetime, tz, question_type, systems)
            VALUES
              ('11111111-1111-4111-8111-111111111111', %s, '2024-01-01T10:00:00', '+07:00', 'career', ARRAY['qimen']),
              ('22222222-2222-4222-8222-222222222222', %s, '2024-01-01T11:00:00', '+07:00', 'career', ARRAY['qimen'])
            """,
            (USER_A, USER_B),
        )
        conn.execute(
            """
            INSERT INTO charts (id, query_id, user_id, he, envelope, cache_key, engine_version)
            VALUES
              ('31111111-1111-4111-8111-111111111111',
               '11111111-1111-4111-8111-111111111111', %s, 'ky_mon', %s::jsonb, 'ck_a', '0.1.0'),
              ('32222222-2222-4222-8222-222222222222',
               '22222222-2222-4222-8222-222222222222', %s, 'luc_nham', %s::jsonb, 'ck_b', '0.1.0')
            """,
            (USER_A, json.dumps(env_a), USER_B, json.dumps(env_b)),
        )
        conn.execute(
            """
            INSERT INTO reports (id, query_id, user_id, interpretation, ai_disclosure)
            VALUES
              ('41111111-1111-4111-8111-111111111111',
               '11111111-1111-4111-8111-111111111111', %s, '{"summary":"a"}'::jsonb, '{"ai":true}'::jsonb),
              ('42222222-2222-4222-8222-222222222222',
               '22222222-2222-4222-8222-222222222222', %s, '{"summary":"b"}'::jsonb, '{"ai":true}'::jsonb)
            """,
            (USER_A, USER_B),
        )
        conn.execute(
            """
            INSERT INTO knowledge_patterns (system, pattern_key, name, conditions)
            VALUES ('qimen', 'qimen_test_pattern', 'Test', '{"all":[]}'::jsonb)
            ON CONFLICT (pattern_key) DO NOTHING
            """
        )
        conn.execute("DELETE FROM app_query_store")
        conn.execute(
            """
            INSERT INTO app_query_store (id, user_id, payload, systems, question_type)
            VALUES
              ('51111111-1111-4111-8111-111111111111', %s, '{"x":1}'::jsonb, ARRAY['qimen'], 'career'),
              ('52222222-2222-4222-8222-222222222222', %s, '{"x":2}'::jsonb, ARRAY['qimen'], 'career')
            """,
            (str(USER_A), str(USER_B)),
        )


@pytest.fixture(scope="module")
def app_dsns(migrated_db: str) -> tuple[str, str, str]:
    app_dsn, admin_dsn = _ensure_app_roles(migrated_db)
    _seed_as_super(migrated_db)
    return migrated_db, app_dsn, admin_dsn


def test_schema_objects_exist(migrated_db: str) -> None:
    tables = [
        "users",
        "queries",
        "charts",
        "knowledge_patterns",
        "reports",
        "audit_logs",
    ]
    with psycopg.connect(migrated_db) as conn:
        for t in tables:
            row = conn.execute(
                "SELECT 1 FROM information_schema.tables "
                "WHERE table_schema = 'public' AND table_name = %s",
                (t,),
            ).fetchone()
            assert row is not None, f"missing table {t}"

        # birth_data_encrypted is bytea; soft-delete column present
        cols = conn.execute(
            """
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name = 'users' AND column_name IN ('birth_data_encrypted', 'deleted_at')
            ORDER BY column_name
            """
        ).fetchall()
        by_name = {r[0]: r[1] for r in cols}
        assert by_name["birth_data_encrypted"] == "bytea"
        assert "deleted_at" in by_name

        # RLS forced on user-scoped tables
        for t in ("users", "queries", "charts", "reports", "audit_logs", "app_query_store"):
            r = conn.execute(
                "SELECT relrowsecurity, relforcerowsecurity FROM pg_class "
                "WHERE relname = %s AND relnamespace = 'public'::regnamespace",
                (t,),
            ).fetchone()
            assert r is not None
            assert r[0] is True and r[1] is True, f"RLS not forced on {t}"

        # GIN indexes
        for idx in (
            "charts_envelope_gin",
            "patterns_conditions_gin",
            "reports_interpretation_gin",
        ):
            r = conn.execute("SELECT 1 FROM pg_indexes WHERE indexname = %s", (idx,)).fetchone()
            assert r is not None, f"missing index {idx}"


def test_fail_closed_unset_guc(app_dsns: tuple[str, str, str]) -> None:
    _, app_dsn, _ = app_dsns
    with psycopg.connect(app_dsn) as conn:
        # No SET LOCAL — must see zero user-scoped rows
        for table in ("charts", "queries", "reports", "app_query_store"):
            n = conn.execute(f"SELECT count(*) FROM {table}").fetchone()
            assert n is not None and n[0] == 0, f"{table} fail-open: saw {n}"


def test_isolation_user_a_cannot_see_b(app_dsns: tuple[str, str, str]) -> None:
    _, app_dsn, _ = app_dsns
    with psycopg.connect(app_dsn) as conn:
        conn.execute("SELECT set_config('app.current_user_id', %s, true)", (str(USER_A),))
        charts = conn.execute("SELECT user_id FROM charts").fetchall()
        assert len(charts) == 1
        assert charts[0][0] == USER_A

        queries = conn.execute("SELECT user_id FROM queries").fetchall()
        assert len(queries) == 1 and queries[0][0] == USER_A

        reports = conn.execute("SELECT user_id FROM reports").fetchall()
        assert len(reports) == 1 and reports[0][0] == USER_A

        store = conn.execute("SELECT user_id FROM app_query_store").fetchall()
        assert len(store) == 1 and store[0][0] == str(USER_A)

        # Update B's chart must affect 0 rows
        cur = conn.execute(
            "UPDATE charts SET engine_version = 'hacked' WHERE user_id = %s",
            (USER_B,),
        )
        assert cur.rowcount == 0
        conn.rollback()


def test_two_user_isolation_as_restricted_role(app_dsns: tuple[str, str, str]) -> None:
    """D-DB-001: user A and user B sessions on strategem_app cannot cross-read."""
    _, app_dsn, _ = app_dsns
    with psycopg.connect(app_dsn) as conn_a:
        conn_a.execute("SELECT set_config('app.current_user_id', %s, true)", (str(USER_A),))
        a_charts = {r[0] for r in conn_a.execute("SELECT id FROM charts").fetchall()}
        assert a_charts == {uuid.UUID("31111111-1111-4111-8111-111111111111")}

    with psycopg.connect(app_dsn) as conn_b:
        conn_b.execute("SELECT set_config('app.current_user_id', %s, true)", (str(USER_B),))
        b_charts = {r[0] for r in conn_b.execute("SELECT id FROM charts").fetchall()}
        assert b_charts == {uuid.UUID("32222222-2222-4222-8222-222222222222")}
        # B must not see A's query store row
        store = conn_b.execute(
            "SELECT id FROM app_query_store WHERE id = %s",
            ("51111111-1111-4111-8111-111111111111",),
        ).fetchall()
        assert store == []


def test_runtime_role_is_not_privileged(app_dsns: tuple[str, str, str]) -> None:
    """strategem_app login must be NOSUPERUSER NOBYPASSRLS (D-DB-001)."""
    from db_schema.runtime_role import connection_is_privileged

    _, app_dsn, _ = app_dsns
    with psycopg.connect(app_dsn) as conn:
        assert connection_is_privileged(conn) is False
        row = conn.execute(
            "SELECT current_user, rolcreatedb FROM pg_roles WHERE oid = current_user::regrole"
        ).fetchone()
        assert row is not None
        assert row[0] == "strategem_app"
        assert row[1] is False


def test_admin_bypass_explicit(app_dsns: tuple[str, str, str]) -> None:
    _, _, admin_dsn = app_dsns
    with psycopg.connect(admin_dsn) as conn:
        # Admin role membership alone is not enough without app.current_role
        conn.execute("SELECT set_config('app.current_user_id', %s, true)", (str(USER_A),))
        # without app.current_role=admin, only owner policy (A's rows) via... wait
        # strategem_admin has app_admin grants; owner policy still applies if GUC is A.
        # Admin policy requires app.current_role = 'admin'.
        n_owner_only = conn.execute("SELECT count(*) FROM charts").fetchone()
        assert n_owner_only is not None and n_owner_only[0] == 1

        conn.execute("SELECT set_config('app.current_role', 'admin', true)")
        n_admin = conn.execute("SELECT count(*) FROM charts").fetchone()
        assert n_admin is not None and n_admin[0] == 2


def test_knowledge_patterns_world_readable(app_dsns: tuple[str, str, str]) -> None:
    _, app_dsn, _ = app_dsns
    with psycopg.connect(app_dsn) as conn:
        # no GUC required for SELECT
        n = conn.execute("SELECT count(*) FROM knowledge_patterns").fetchone()
        assert n is not None and n[0] >= 1
        # write denied for app_user (table privilege and/or RLS policy)
        with pytest.raises(psycopg.Error):
            conn.execute(
                """
                INSERT INTO knowledge_patterns (system, pattern_key, name, conditions)
                VALUES ('qimen', 'should_fail', 'x', '{}'::jsonb)
                """
            )
            conn.commit()
        conn.rollback()


def test_gin_index_used_for_containment(app_dsns: tuple[str, str, str]) -> None:
    super_dsn, _, _ = app_dsns
    # Tiny tables prefer seq scan; disable it so EXPLAIN proves the GIN is usable.
    with psycopg.connect(super_dsn) as conn:
        conn.execute("SET enable_seqscan = off")
        plan = conn.execute(
            """
            EXPLAIN (FORMAT JSON)
            SELECT id FROM charts WHERE envelope @> '{"he":"ky_mon"}'::jsonb
            """
        ).fetchone()
        assert plan is not None
        blob: Any = plan[0]
        text = json.dumps(blob)
        assert "Bitmap" in text or "charts_envelope_gin" in text or "Index" in text, (
            f"expected GIN/index plan, got: {text}"
        )
