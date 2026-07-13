"""COV-002: LocalEngineClient stamps co_truong_phai + co_lich_phap for all he."""

from __future__ import annotations

from tamthuc_api.clients.engine import LocalEngineClient


def test_local_engine_stamps_all_three_systems() -> None:
    eng = LocalEngineClient(cast_cli=None)  # force local path
    for system, he in (
        ("qimen", "ky_mon"),
        ("liuren", "luc_nham"),
        ("taiyi", "thai_at"),
    ):
        out = eng.cast(
            system,
            {
                "datetime": "2004-01-01T10:30:00",
                "tz": "+07:00",
                "kinh_do": 106.7,
            },
        )
        assert out["he"] == he
        assert out.get("co_truong_phai"), f"{system} missing co_truong_phai"
        clp = (out.get("lich_phap") or {}).get("co_lich_phap")
        assert isinstance(clp, dict), f"{system} missing co_lich_phap"
        assert clp.get("stamped") is True
