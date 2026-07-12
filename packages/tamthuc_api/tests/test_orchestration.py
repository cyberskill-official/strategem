from __future__ import annotations

from fastapi.testclient import TestClient
from tamthuc_api.app import create_app
from tamthuc_api.clients.rag import StubRagClient
from tamthuc_api.clients.rule import StubRuleClient
from tamthuc_api.orchestrator import Orchestrator


def test_qimen_flow_sequence_and_passthrough() -> None:
    rule = StubRuleClient()
    rag = StubRagClient()
    orch = Orchestrator(rule=rule, rag=rag)
    client = TestClient(create_app(orch))
    r = client.post(
        "/api/v1/calculate/qimen",
        json={"datetime": "2004-01-01T10:30:00", "longitude": 106.7, "question": "q"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["ai_disclosure"]["is_ai_generated"] is True
    assert "qimen" in body["charts"]
    assert body["charts"]["qimen"]["envelope_version"] == 1
    # sequence core -> engine -> rule -> rag
    assert orch.call_log[:4] == ["core", "engine", "rule", "rag"]
    # same envelope to rule and rag
    assert rule.last_envelope is not None
    assert rag.last_envelope == rule.last_envelope
    assert body["charts"]["qimen"] is not None


def test_calculate_all_forbidden_for_free() -> None:
    client = TestClient(create_app())
    r = client.post(
        "/api/v1/calculate/all",
        json={"datetime": "2004-01-01T10:30:00", "tier": "free"},
    )
    assert r.status_code == 403
    assert r.json()["error"]["code"] == "FORBIDDEN_TIER"


def test_calculate_all_premium() -> None:
    client = TestClient(create_app())
    r = client.post(
        "/api/v1/calculate/all",
        json={"datetime": "2004-01-01T10:30:00", "tier": "premium"},
    )
    assert r.status_code == 200
    assert set(r.json()["charts"]) == {"qimen", "liuren", "taiyi"}
