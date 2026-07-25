"""COV-027: local compose + Dockerfile contracts (static, no daemon required)."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def test_local_compose_builds_not_ghcr() -> None:
    text = (ROOT / "deploy/compose/docker-compose.local.yml").read_text()
    assert "build:" in text
    assert "dockerfile: deploy/docker/api.Dockerfile" in text
    assert "dockerfile: deploy/docker/web.Dockerfile" in text
    assert "ghcr.io" not in text
    assert "postgres" in text
    assert "CAST_CLI" in text
    assert "READY_REQUIRE_CAST_CLI" in text
    assert "host.docker.internal" in text
    # COV-009/027: web must reach API on compose DNS, not host-published URL
    assert "API_URL" in text
    assert "http://api:8000" in text
    # Phase 4: auto-migrate before API; no unused redis false confidence
    assert "migrate:" in text
    assert "db_schema.migrate" in text
    assert "service_completed_successfully" in text
    assert "redis:" not in text
    assert "PAYMENTS_MODE" in text
    assert "READY_REQUIRE_LLM" in text


def test_local_up_script_exists() -> None:
    script = ROOT / "scripts/local-up.sh"
    assert script.is_file()
    body = script.read_text()
    assert "docker compose" in body
    assert "/healthz" in body
    assert "/ready" in body


def test_api_dockerfile_runs_cast_cli_and_api() -> None:
    text = (ROOT / "deploy/docker/api.Dockerfile").read_text()
    assert "cast-cli" in text
    assert "python -m tamthuc_api" in text or '["python", "-m", "tamthuc_api"]' in text


def test_web_dockerfile_bakes_server_api_url() -> None:
    text = (ROOT / "deploy/docker/web.Dockerfile").read_text()
    assert "API_URL" in text
    assert "http://api:8000" in text


def test_local_runbook_exists() -> None:
    p = ROOT / "docs/deploy/local-docker-lmstudio.md"
    assert p.is_file()
    body = p.read_text()
    assert "LMStudio" in body or "LM Studio" in body or "1234" in body
    assert "docker-compose.local.yml" in body
