"""Golden ban shape contracts for web chart adapters."""

from __future__ import annotations

from fastapi.testclient import TestClient
from tamthuc_api.app import create_app

PAYLOAD = {
    "datetime": "2004-01-01T10:30:00",
    "tz": "+07:00",
    "longitude": 105.85,
    "place": "Ha Noi",
    "question_type": "trach_thoi",
    "persona_level": "beginner",
}


def test_qimen_ban_shape() -> None:
    client = TestClient(create_app())
    r = client.post("/api/v1/calculate/qimen", json={**PAYLOAD, "systems": ["qimen"]})
    assert r.status_code == 200
    ban = r.json()["charts"]["qimen"]["ban"]
    assert len(ban["dia_ban"]) == 9
    assert len(ban["thien_ban"]) == 9
    assert "cuu_tinh" in ban
    assert "bat_mon" in ban


def test_liuren_ban_shape() -> None:
    client = TestClient(create_app())
    r = client.post("/api/v1/calculate/liuren", json={**PAYLOAD, "systems": ["liuren"]})
    assert r.status_code == 200
    ban = r.json()["charts"]["liuren"]["ban"]
    tdb = ban.get("thien_dia_ban") or {}
    # local engine or CLI both should expose 12-plate data
    dia = tdb.get("dia") or ban.get("dia") or []
    thien = tdb.get("thien") or ban.get("thien") or []
    assert len(dia) == 12 or "tu_khoa" in ban
    if len(dia) == 12:
        assert len(thien) == 12
    assert "tu_khoa" in ban or "tam_truyen" in ban


def test_taiyi_ban_shape() -> None:
    client = TestClient(create_app())
    r = client.post("/api/v1/calculate/taiyi", json={**PAYLOAD, "systems": ["taiyi"]})
    assert r.status_code == 200
    ban = r.json()["charts"]["taiyi"]["ban"]
    assert any(k in ban for k in ("thai_at_cung", "thai_at_ring", "thap_luc_than", "tich"))
