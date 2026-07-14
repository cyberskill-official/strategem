"""E2E cast path: calculate → persist → GET query (+ report + history)."""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from tamthuc_api.app import create_app


def test_qimen_cast_persist_and_fetch() -> None:
    client = TestClient(create_app())
    r = client.post(
        "/api/v1/calculate/qimen",
        json={
            "datetime": "2004-01-01T10:30:00",
            "tz": "+07:00",
            "longitude": 106.7,
            "question": "timing",
            "question_type": "trach_thoi",
            "co_truong_phai": {"dingju_method": "chaibu", "pan_method": "zhuan"},
        },
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["query_id"]
    assert "qimen" in body["charts"]
    chart = body["charts"]["qimen"]
    assert chart["he"] == "ky_mon"
    ban = chart["ban"]
    assert isinstance(ban.get("dia_ban"), list) and len(ban["dia_ban"]) == 9
    assert isinstance(ban.get("thien_ban"), list)
    assert body["patterns"]
    assert body["ai_disclosure"] is not None
    # Interpretation is either released (beginner/expert) or high-stakes withheld
    # (stable keys + summary). Soft review still releases beginner text.
    interp = body["interpretation"]
    assert isinstance(interp, dict)
    beginner = interp.get("beginner") or interp.get("summary")
    assert beginner, f"expected beginner or summary, got keys={list(interp.keys())}"
    assert body.get("report_id")
    assert body.get("report", {}).get("report_id") == body["report_id"]

    qid = body["query_id"]
    g = client.get(f"/api/v1/queries/{qid}")
    assert g.status_code == 200
    got = g.json()
    assert got["query_id"] == qid
    assert got["charts"]["qimen"]["ban"]["dia_ban"] == ban["dia_ban"]
    got_interp = got["interpretation"] or {}
    got_beginner = got_interp.get("beginner") or got_interp.get("summary")
    assert got_beginner == beginner

    rid = body["report_id"]
    gr = client.get(f"/api/v1/reports/{rid}")
    assert gr.status_code == 200
    report = gr.json()
    assert report["report_id"] == rid
    assert report["query_id"] == qid
    assert "chart_summary" in report

    hist = client.get("/api/v1/queries")
    assert hist.status_code == 200
    items = hist.json()["items"]
    assert any(i["query_id"] == qid for i in items)

    pdf = client.get(f"/api/v1/reports/{rid}/pdf")
    assert pdf.status_code == 200
    assert "pdf" in pdf.headers.get("content-type", "")


def test_query_not_found() -> None:
    client = TestClient(create_app())
    r = client.get("/api/v1/queries/does-not-exist")
    assert r.status_code == 404


def test_healthz() -> None:
    client = TestClient(create_app())
    assert client.get("/healthz").json()["status"] == "ok"


def test_ready_default_ok_with_local_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("CAST_CLI", raising=False)
    monkeypatch.delenv("READY_REQUIRE_CAST_CLI", raising=False)
    client = TestClient(create_app())
    r = client.get("/ready")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert body["checks"]["cast_cli_configured"] is False
    assert body["checks"]["cast_cli_present"] is False
    assert body["checks"]["engine_mode"] == "local_fallback"


def test_ready_strict_cast_cli_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("CAST_CLI", raising=False)
    monkeypatch.setenv("READY_REQUIRE_CAST_CLI", "1")
    client = TestClient(create_app())
    r = client.get("/ready")
    assert r.status_code == 503
    assert r.json()["status"] == "not_ready"


def test_ready_with_executable_cast_cli(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    cli = tmp_path / "cast-cli"
    cli.write_text("#!/bin/sh\necho '{}'\n", encoding="utf-8")
    cli.chmod(0o755)
    monkeypatch.setenv("CAST_CLI", str(cli))
    monkeypatch.delenv("READY_REQUIRE_CAST_CLI", raising=False)
    client = TestClient(create_app())
    r = client.get("/ready")
    assert r.status_code == 200
    body = r.json()
    assert body["checks"]["cast_cli_configured"] is True
    assert body["checks"]["cast_cli_present"] is True
    assert body["checks"]["engine_mode"] == "cast_cli"
