from __future__ import annotations

from typing import Any, Protocol


class EngineClient(Protocol):
    def cast(self, system: str, lich_phap: dict[str, Any]) -> dict[str, Any]: ...


class StubEngineClient:
    def cast(self, system: str, lich_phap: dict[str, Any]) -> dict[str, Any]:
        he = {"qimen": "ky_mon", "liuren": "luc_nham", "taiyi": "thai_at"}.get(system, system)
        return {
            "envelope_version": 1,
            "he": he,
            "lich_phap": lich_phap,
            "ban": {"stub": True},
            "cach_cuc": [],
            "co_truong_phai": {},
            "dau_vao": {},
            "provenance": {"engine": system, "engine_version": "0.1.0"},
        }
