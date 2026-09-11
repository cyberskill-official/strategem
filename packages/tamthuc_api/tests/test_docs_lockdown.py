"""OpenAPI /docs lockdown outside local/test (production readiness)."""

from __future__ import annotations

from fastapi.testclient import TestClient
from tamthuc_api.app import create_app
from tamthuc_api.authz import api_docs_enabled, is_public_path


def test_api_docs_enabled_local(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setenv("ENV", "development")
    monkeypatch.setenv("APP_ENV", "development")
    monkeypatch.delenv("ENABLE_API_DOCS", raising=False)
    assert api_docs_enabled() is True


def test_api_docs_disabled_production(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    # Autouse conftest sets ENV=test; override both so is_local_or_test_env is false.
    monkeypatch.setenv("ENV", "production")
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.delenv("ENABLE_API_DOCS", raising=False)
    assert api_docs_enabled() is False
    assert is_public_path("/docs") is False
    assert is_public_path("/openapi.json") is False
    assert is_public_path("/healthz") is True


def test_docs_routes_absent_when_flag_off(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setenv("ENV", "test")
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv("ENABLE_API_DOCS", "0")
    app = create_app(enable_rate_limit=False)
    client = TestClient(app)
    # Not public when disabled → auth middleware 401; or FastAPI 404 if route absent.
    for path in ("/docs", "/openapi.json", "/redoc"):
        assert client.get(path).status_code in {401, 404}


def test_docs_routes_present_when_enabled(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setenv("ENV", "test")
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv("ENABLE_API_DOCS", "1")
    app = create_app(enable_rate_limit=False)
    client = TestClient(app)
    assert client.get("/openapi.json").status_code == 200
