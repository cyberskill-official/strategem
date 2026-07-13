"""COV-020..026 productization tests (ops, metrics, graph, payments, pdf-related hooks)."""

from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient
from tamthuc_api.app import create_app
from tamthuc_api.observability.metrics import MetricsRegistry, render_prometheus

ROOT = Path(__file__).resolve().parents[3]


def test_staging_runbook_and_smoke_script_exist() -> None:
    assert (ROOT / "docs/deploy/staging-runbook.md").is_file()
    assert (ROOT / "scripts/smoke-staging.sh").is_file()
    text = (ROOT / "deploy/compose/docker-compose.staging.yml").read_text()
    assert "READY_REQUIRE_CAST_CLI" in text
    assert "CAST_CLI" in text
    assert "NEXT_PUBLIC_API_BASE" in text or "web" in text


def test_metrics_cast_latency_and_ready_failure() -> None:
    reg = MetricsRegistry()
    reg.record_cast(0.12, system="qimen", engine_mode="local", ok=True)
    reg.record_cast(0.4, system="liuren", engine_mode="cast_cli", ok=False)
    reg.record_ready_failure("cast_cli_missing")
    body = render_prometheus(reg)
    assert "cast_latency_seconds" in body
    assert "cast_total" in body
    assert "ready_failures_total" in body
    assert "qimen" in body


def test_metrics_endpoint() -> None:
    client = TestClient(create_app())
    # trigger a cast to populate metrics
    client.post(
        "/api/v1/calculate/qimen",
        json={
            "datetime": "2004-01-01T10:30:00",
            "tz": "+07:00",
            "longitude": 106.7,
            "systems": ["qimen"],
        },
    )
    r = client.get("/metrics")
    assert r.status_code == 200
    assert "cast_" in r.text or "chart_gen" in r.text


def test_graph_neighbors_stored_only() -> None:
    client = TestClient(create_app())
    r = client.get("/api/v1/knowledge/graph/neighbors?node_id=ngu_hanh_moc")
    assert r.status_code == 200, r.text
    body = r.json()
    assert body.get("source") == "stored_graph_only"
    assert body.get("found") is True
    assert body.get("neighbors")
    # no invented edges: every neighbor has a known rel
    for n in body["neighbors"]:
        assert n["rel"] in {"sinh", "khac"}


def test_payment_single_rail_checkout_and_webhook() -> None:
    client = TestClient(create_app())
    prov = client.get("/api/v1/payments/provider").json()
    assert prov["provider"] == "stripe"
    assert prov["single_rail"] is True
    assert prov["free_cast_remains"] is True

    co = client.post(
        "/api/v1/payments/checkout",
        json={"user_id": "u-pay-1", "email": "a@example.com"},
    )
    assert co.status_code == 200, co.text
    session = co.json()["checkout_session"]
    assert session["object"] == "checkout.session"
    sid = session["id"]

    wh = client.post(
        "/api/v1/payments/webhook",
        json={
            "type": "checkout.session.completed",
            "data": {"object": {"id": sid, "client_reference_id": "u-pay-1"}},
        },
    )
    assert wh.status_code == 200, wh.text
    assert wh.json()["tier"] == "premium"
    tier = client.get("/api/v1/payments/tier/u-pay-1").json()
    assert tier["tier"] == "premium"


def test_coverage_gate_script_exists() -> None:
    """COV-025: coverage gate is tracked under scripts/ (not .cyberos/, which is gitignored)."""
    p = ROOT / "scripts/coverage-gate.sh"
    assert p.is_file()
    text = p.read_text()
    assert "COVERAGE_MIN" in text or "90" in text
    # Optional local gates.env (cyberos init) — never required on CI
    gates = ROOT / ".cyberos/gates.env"
    if gates.is_file():
        g = gates.read_text()
        assert "coverage-gate" in g or "COVERAGE_CMD" in g or "COVERAGE_MIN" in g


def test_playwright_journey_config_exists() -> None:
    assert (ROOT / "apps/web/playwright.config.ts").is_file()
    assert (ROOT / "apps/web/tests/e2e/journeys.spec.ts").is_file()
    assert (ROOT / ".github/workflows/product-journeys.yml").is_file()
