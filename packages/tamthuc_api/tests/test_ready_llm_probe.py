"""READY_REQUIRE_LLM readiness gate."""

from __future__ import annotations

from fastapi.testclient import TestClient
from tamthuc_api.app import create_app


def test_ready_includes_llm_checks_without_failing(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.delenv("READY_REQUIRE_CAST_CLI", raising=False)
    monkeypatch.delenv("READY_REQUIRE_LLM", raising=False)
    monkeypatch.setenv("LLM_BACKEND", "stub")
    client = TestClient(create_app())
    r = client.get("/ready")
    assert r.status_code == 200
    body = r.json()
    assert "llm_backend" in body["checks"]
    assert "degraded" in body


def test_ready_fails_when_llm_required_and_unreachable(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.delenv("READY_REQUIRE_CAST_CLI", raising=False)
    monkeypatch.setenv("READY_REQUIRE_LLM", "1")
    monkeypatch.setenv("LLM_BACKEND", "openai_compatible")
    monkeypatch.setenv("LLM_BASE_URL", "http://127.0.0.1:1/v1")
    client = TestClient(create_app())
    r = client.get("/ready")
    assert r.status_code == 503
    assert r.json()["status"] == "not_ready"
