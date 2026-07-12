"""E2E cast path: calculate → persist → GET query."""

from __future__ import annotations

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
    assert body["ai_disclosure"]["is_ai_generated"] is True
    assert body["interpretation"]["beginner"]

    qid = body["query_id"]
    g = client.get(f"/api/v1/queries/{qid}")
    assert g.status_code == 200
    got = g.json()
    assert got["query_id"] == qid
    assert got["charts"]["qimen"]["ban"]["dia_ban"] == ban["dia_ban"]
    assert got["interpretation"]["beginner"] == body["interpretation"]["beginner"]


def test_query_not_found() -> None:
    client = TestClient(create_app())
    r = client.get("/api/v1/queries/does-not-exist")
    assert r.status_code == 404


def test_healthz() -> None:
    client = TestClient(create_app())
    assert client.get("/healthz").json()["status"] == "ok"
