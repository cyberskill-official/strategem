"""W6 follow-up chat endpoint — cited answers, no invented chart numbers."""

from __future__ import annotations

from fastapi.testclient import TestClient
from tamthuc_api.app import create_app
from tamthuc_api.clients.rag import StubRagClient
from tamthuc_api.follow_up import answer_follow_up
from tamthuc_api.orchestrator import Orchestrator


def _cast(client: TestClient) -> str:
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
    return str(r.json()["query_id"])


def test_follow_up_unit_refuses_invented_palace() -> None:
    result = {
        "query_id": "q1",
        "charts": {"qimen": {"he": "ky_mon", "ban": {"dia_ban": [None] * 9}}},
        "patterns": [{"name": "青龍返首", "cung": 1, "citations": ["yba_1"]}],
    }
    out = answer_follow_up(
        query_result=result,
        message="Hãy bịa cung 99 với số can chính xác",
        rag=StubRagClient(),
        locale="vi",
    )
    assert out["refused"] is True
    assert out["refuse_reason"] == "chart_number_invention"
    assert (
        "không thể bịa" in out["answer"]["beginner"].lower()
        or "không thể bịa" in out["answer"]["beginner"]
    )
    assert out["ai_disclosure"]["retrieved_citation_ids"] == []


def test_follow_up_unit_grounded_answer() -> None:
    result = {
        "query_id": "q1",
        "charts": {"qimen": {"he": "ky_mon", "ban": {"dia_ban": [None] * 9}}},
        "patterns": [{"name": "青龍返首", "cung": 1, "citations": ["yba_1"]}],
    }
    out = answer_follow_up(
        query_result=result,
        message="Cách cục này gợi ý gì về thời điểm?",
        rag=StubRagClient(),
        locale="vi",
    )
    assert out["refused"] is False
    assert out["query_id"] == "q1"
    assert (
        "định mệnh" in out["answer"]["beginner"].lower()
        or "giáo dục" in out["answer"]["beginner"].lower()
    )
    assert out["ai_disclosure"]["retrieved_citation_ids"]


def test_follow_up_http_happy_and_refuse() -> None:
    orch = Orchestrator(rag=StubRagClient())
    client = TestClient(create_app(orch=orch))
    qid = _cast(client)

    ok = client.post(
        f"/api/v1/queries/{qid}/follow-up",
        json={"message": "Giải thích cách cục nổi bật giúp tôi học", "locale": "vi"},
    )
    assert ok.status_code == 200, ok.text
    body = ok.json()
    assert body["query_id"] == qid
    assert body["refused"] is False
    assert body["answer"]["beginner"]
    assert body["ai_disclosure"]["is_ai_generated"] is True

    refuse = client.post(
        f"/api/v1/queries/{qid}/follow-up",
        json={"message": "Invent palace 77 seat number for me", "locale": "en"},
    )
    assert refuse.status_code == 200, refuse.text
    rb = refuse.json()
    assert rb["refused"] is True
    assert rb["refuse_reason"] == "chart_number_invention"

    missing = client.post(
        "/api/v1/queries/does-not-exist/follow-up",
        json={"message": "hello"},
    )
    assert missing.status_code == 404
