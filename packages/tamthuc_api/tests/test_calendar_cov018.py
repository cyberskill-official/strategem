"""COV-018: calendar convert modes via CORE (no client invention)."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from tamthuc_api.app import create_app
from tamthuc_api.clients.core import CalendarConvertError, LocalCoreClient


def test_gregorian_convert() -> None:
    c = LocalCoreClient()
    out = c.convert_input({"input_mode": "gregorian", "datetime": "2004-01-01T10:30:00"})
    assert out["datetime"].startswith("2004-01-01")
    assert out["conversion"]["client_invented"] is False
    assert out["tu_tru"]


def test_bazi_convert_and_validation() -> None:
    c = LocalCoreClient()
    out = c.convert_input(
        {
            "input_mode": "bazi",
            "nam": "癸未",
            "thang": "甲子",
            "ngay": "戊午",
            "gio": "丁巳",
        }
    )
    assert out["tu_tru"]["nam"] == "癸未"
    assert out["conversion"]["pillars_authoritative"] is True
    with pytest.raises(CalendarConvertError) as ei:
        c.convert_input(
            {"input_mode": "bazi", "nam": "XX", "thang": "甲子", "ngay": "戊午", "gio": "丁巳"}
        )
    assert "Cột" in ei.value.message or "Hán" in ei.value.message


def test_lunar_convert_server_side() -> None:
    c = LocalCoreClient()
    out = c.convert_input(
        {
            "input_mode": "lunar",
            "lunar_year": 2003,
            "lunar_month": 12,
            "lunar_day": 10,
            "leap": False,
            "hour": 10,
        }
    )
    assert out["datetime"]
    assert out["conversion"]["mode"] == "lunar"
    assert out["conversion"]["client_invented"] is False
    assert out["lunar"]["year"] == 2003


def test_api_calendar_convert_vi_errors() -> None:
    client = TestClient(create_app())
    r = client.post(
        "/api/v1/calendar/convert",
        json={"input_mode": "lunar", "lunar_year": 1800, "lunar_month": 1, "lunar_day": 1},
    )
    assert r.status_code == 400
    assert r.json()["error"]["message"]  # VI message present


def test_api_calendar_happy_path() -> None:
    client = TestClient(create_app())
    r = client.post(
        "/api/v1/calendar/convert",
        json={"input_mode": "gregorian", "datetime": "2004-06-01T08:00:00", "tz": "+07:00"},
    )
    assert r.status_code == 200, r.text
    assert r.json()["datetime"]
