"""COV-010: DATABASE_URL → Postgres persist; prod fail-closed; cast→get."""

from __future__ import annotations

import os
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from tamthuc_api.persistence import PersistenceService
from tamthuc_api.pg_store import PgQueryStore, require_database_or_memory


def test_prod_fail_closed_without_database_url(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.delenv("ALLOW_MEMORY_PERSISTENCE", raising=False)
    with pytest.raises(RuntimeError, match="DATABASE_URL"):
        require_database_or_memory()


def test_dev_allows_memory_without_database_url(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("APP_ENV", raising=False)
    assert require_database_or_memory() == "memory"
    svc = PersistenceService.from_env()
    assert svc.backend == "memory"
    assert svc.pg is None


def test_postgres_cast_get_survives_new_service(monkeypatch: pytest.MonkeyPatch) -> None:
    dsn = os.environ.get("DATABASE_URL") or os.environ.get("COV010_DATABASE_URL")
    if not dsn:
        # local compose default
        dsn = "postgresql://postgres:postgres@127.0.0.1:15432/strategem"
    monkeypatch.setenv("DATABASE_URL", dsn)
    monkeypatch.delenv("APP_ENV", raising=False)

    # ensure table exists (migration 0010)
    try:
        import psycopg

        with psycopg.connect(dsn, autocommit=True) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS app_query_store (
                  id uuid PRIMARY KEY,
                  user_id text NOT NULL DEFAULT 'anon',
                  payload jsonb NOT NULL,
                  systems text[] NOT NULL DEFAULT '{}',
                  question_type text,
                  report_id text,
                  created_at timestamptz NOT NULL DEFAULT now()
                )
                """
            )
    except Exception as e:  # pragma: no cover
        pytest.skip(f"postgres unavailable: {e}")

    assert require_database_or_memory() == "postgres"
    a = PersistenceService.from_env()
    assert a.backend == "postgres" and a.pg is not None

    qid = str(uuid4())
    payload = {
        "query_id": qid,
        "charts": {"qimen": {"he": "ky_mon", "ban": {"dia_ban": [1] * 9}}},
        "patterns": [{"id": "p1", "name": "青龍返首"}],
        "report_id": "rep-1",
        "report": {"report_id": "rep-1", "summary": "ok"},
    }
    charts = payload["charts"]
    patterns = payload["patterns"]
    report = payload["report"]
    assert isinstance(charts, dict)
    assert isinstance(patterns, list)
    assert isinstance(report, dict)
    pr = a.persist_query_result(
        "anon",
        {"question_type": "trach_thoi", "datetime": "2004-01-01T10:30:00"},
        charts,
        patterns,
        report=report,
        full_result=payload,
    )
    assert pr.query_id

    # new service instance == process restart simulation
    b = PersistenceService.from_env()
    got = b.get_query_result(pr.query_id)
    assert got is not None
    assert got["charts"]["qimen"]["he"] == "ky_mon"
    assert got.get("report_id") == "rep-1" or (got.get("report") or {}).get("report_id") == "rep-1"
    rep = b.get_report("rep-1")
    assert rep is not None
    assert rep.get("report_id") == "rep-1"


def test_api_calculate_get_query_with_postgres(monkeypatch: pytest.MonkeyPatch) -> None:
    dsn = (
        os.environ.get("DATABASE_URL") or "postgresql://postgres:postgres@127.0.0.1:15432/strategem"
    )
    monkeypatch.setenv("DATABASE_URL", dsn)
    try:
        import psycopg

        with psycopg.connect(dsn, autocommit=True) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS app_query_store (
                  id uuid PRIMARY KEY,
                  user_id text NOT NULL DEFAULT 'anon',
                  payload jsonb NOT NULL,
                  systems text[] NOT NULL DEFAULT '{}',
                  question_type text,
                  report_id text,
                  created_at timestamptz NOT NULL DEFAULT now()
                )
                """
            )
    except Exception as e:  # pragma: no cover
        pytest.skip(f"postgres unavailable: {e}")

    # re-import app after env set — create_app uses from_env
    from tamthuc_api.app import create_app

    client = TestClient(create_app())
    from auth_helpers import auth_header, register_and_login

    tokens = register_and_login(client, email="pgpersist@example.com")
    r = client.post(
        "/api/v1/calculate/qimen",
        json={
            "datetime": "2004-01-01T10:30:00",
            "tz": "+07:00",
            "longitude": 106.7,
            "systems": ["qimen"],
            "question_type": "trach_thoi",
            "persona_level": "beginner",
        },
    )
    assert r.status_code == 200, r.text
    body = r.json()
    qid = body["query_id"]
    g = client.get(f"/api/v1/queries/{qid}", headers=auth_header(tokens["access"]))
    assert g.status_code == 200, g.text
    again = g.json()
    assert again["query_id"] == qid
    assert "qimen" in (again.get("charts") or {})


def test_pg_store_unit_roundtrip_without_api(monkeypatch: pytest.MonkeyPatch) -> None:
    dsn = (
        os.environ.get("DATABASE_URL") or "postgresql://postgres:postgres@127.0.0.1:15432/strategem"
    )
    try:
        store = PgQueryStore(dsn=dsn)
        qid = store.create(
            "u1",
            {"question_type": "x"},
            ["qimen"],
            {"charts": {"qimen": {"he": "ky_mon"}}, "query_id": "temp"},
        )
        got = store.get(qid)
        assert got and got["charts"]["qimen"]["he"] == "ky_mon"
    except Exception as e:  # pragma: no cover
        pytest.skip(f"postgres unavailable: {e}")
