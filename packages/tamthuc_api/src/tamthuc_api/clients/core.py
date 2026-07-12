"""Calendar / lich phap client — FR-API-001."""

from __future__ import annotations

from datetime import datetime
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


class LocalCoreClient:
    """Pass-through lich_phap stamp used by LocalEngineClient (no re-cast of ban)."""

    def tinh_lich_phap(self, payload: dict[str, Any]) -> dict[str, Any]:
        dt = str(payload.get("datetime") or "")
        year = month = day = hour = ""
        try:
            parsed = datetime.fromisoformat(dt.replace("Z", "+00:00")[:19])
            # simple ganzhi placeholders from ordinal (not full CORE tables)
            stems = "甲乙丙丁戊己庚辛壬癸"
            branches = "子丑寅卯辰巳午未申酉戌亥"
            y = stems[parsed.year % 10] + branches[parsed.year % 12]
            m = stems[parsed.month % 10] + branches[parsed.month % 12]
            d = stems[parsed.day % 10] + branches[parsed.day % 12]
            h = stems[parsed.hour % 10] + branches[(parsed.hour // 2) % 12]
            year, month, day, hour = y, m, d, h
        except ValueError:
            year, month, day, hour = "甲子", "丙寅", "戊午", "甲子"

        return {
            "datetime": dt,
            "tz": payload.get("tz", "+07:00"),
            "kinh_do": payload.get("kinh_do")
            if payload.get("kinh_do") is not None
            else payload.get("longitude", 106.7),
            "question_type": payload.get("question_type")
            or payload.get("loai_cau_hoi")
            or "trach_thoi",
            "co_truong_phai": payload.get("co_truong_phai") or {},
            "flags": payload.get("flags") or {},
            "tu_tru": {"nam": year, "thang": month, "ngay": day, "gio": hour},
            "year": year,
            "month": month,
            "day": day,
            "hour": hour,
            "chan_thai_duong": True,
            "co_lich_phap": {
                "use_true_solar_time": True,
                "longitude": payload.get("kinh_do")
                if payload.get("kinh_do") is not None
                else payload.get("longitude", 106.7),
            },
        }
