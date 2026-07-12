from __future__ import annotations

from typing import Any, Protocol


class CoreClient(Protocol):
    def tinh_lich_phap(self, payload: dict[str, Any]) -> dict[str, Any]: ...


class StubCoreClient:
    def tinh_lich_phap(self, payload: dict[str, Any]) -> dict[str, Any]:
        return {
            "year": "甲子",
            "month": "丙寅",
            "day": "戊午",
            "hour": "甲子",
            "co_lich_phap": payload.get("flags", {}),
            "chan_thai_duong": True,
        }
