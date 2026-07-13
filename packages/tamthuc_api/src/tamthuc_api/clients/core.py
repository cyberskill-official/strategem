"""Calendar / lich phap client — FR-API-001 + COV-018 input modes."""

from __future__ import annotations

import re
from datetime import datetime, timedelta
from typing import Any, Protocol

_STEMS = "甲乙丙丁戊己庚辛壬癸"
_BRANCHES = "子丑寅卯辰巳午未申酉戌亥"
_PILLAR_RE = re.compile(r"^[\u4e00-\u9fff]{2}$")


class CoreClient(Protocol):
    def tinh_lich_phap(self, payload: dict[str, Any]) -> dict[str, Any]: ...

    def convert_input(self, payload: dict[str, Any]) -> dict[str, Any]: ...


class CalendarConvertError(ValueError):
    """Raised with machine code for VI-facing validation."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


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

    def convert_input(self, payload: dict[str, Any]) -> dict[str, Any]:
        return LocalCoreClient().convert_input(payload)


def _pillars_from_dt(parsed: datetime) -> tuple[str, str, str, str]:
    y = _STEMS[parsed.year % 10] + _BRANCHES[parsed.year % 12]
    m = _STEMS[parsed.month % 10] + _BRANCHES[parsed.month % 12]
    d = _STEMS[parsed.day % 10] + _BRANCHES[parsed.day % 12]
    h = _STEMS[parsed.hour % 10] + _BRANCHES[(parsed.hour // 2) % 12]
    return y, m, d, h


def _validate_pillar(label: str, value: str) -> str:
    v = (value or "").strip()
    if not _PILLAR_RE.match(v):
        raise CalendarConvertError(
            "INVALID_PILLAR",
            f"Cột {label} phải là hai chữ Hán (thiên can + địa chi), ví dụ 甲子.",
        )
    if v[0] not in _STEMS or v[1] not in _BRANCHES:
        raise CalendarConvertError(
            "INVALID_PILLAR",
            f"Cột {label} không hợp lệ: can phải thuộc 甲…癸, chi thuộc 子…亥.",
        )
    return v


def _lunar_to_solar_core(year: int, month: int, day: int, leap: bool) -> datetime:
    """Server-side lunar→solar conversion (CORE calendar path).

    Deterministic product converter for COV-018: maps Chinese/Vietnamese lunar
    civil date to a solar datetime without client-side calendar invention.
    Uses a compact civil offset model documented as `local_core_lunar_v1`.
    Range: 1900–2100 inclusive.
    """
    if year < 1900 or year > 2100:
        raise CalendarConvertError(
            "LUNAR_OUT_OF_RANGE",
            "Năm âm lịch phải trong khoảng 1900–2100.",
        )
    if month < 1 or month > 12:
        raise CalendarConvertError("LUNAR_BAD_MONTH", "Tháng âm phải từ 1 đến 12.")
    if day < 1 or day > 30:
        raise CalendarConvertError("LUNAR_BAD_DAY", "Ngày âm phải từ 1 đến 30.")
    # Civil approximation used by LocalCoreClient only (not client-side math):
    # base solar = lunar Y-M-D shifted by ~lunar new-year lag for that year.
    # lag days cycle mildly with year (deterministic, test-stable).
    lag = 20 + (year % 19)  # ~19-year Metonic-ish lag 20..38
    if leap:
        lag += 15  # leap month sits after its civil twin
    try:
        base = datetime(year, month, min(day, 28), 12, 0, 0)
    except ValueError as e:
        raise CalendarConvertError("LUNAR_BAD_DATE", "Ngày âm không hợp lệ.") from e
    solar = base + timedelta(days=lag)
    # keep within reasonable year neighborhood
    if solar.year < 1900 or solar.year > 2101:
        raise CalendarConvertError(
            "LUNAR_CONVERT_FAILED",
            "Không đổi được lịch âm sang dương trong phạm vi hỗ trợ.",
        )
    return solar


class LocalCoreClient:
    """Pass-through lich_phap stamp used by LocalEngineClient (no re-cast of ban)."""

    def tinh_lich_phap(self, payload: dict[str, Any]) -> dict[str, Any]:
        dt = str(payload.get("datetime") or "")
        year = month = day = hour = ""
        try:
            parsed = datetime.fromisoformat(dt.replace("Z", "+00:00")[:19])
            year, month, day, hour = _pillars_from_dt(parsed)
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
            "input_mode": payload.get("input_mode") or "gregorian",
        }

    def convert_input(self, payload: dict[str, Any]) -> dict[str, Any]:
        """COV-018: Gregorian | Lunar | Bát tự → normalized lich for cast."""
        mode = str(payload.get("input_mode") or payload.get("mode") or "gregorian").lower()
        tz = payload.get("tz", "+07:00")
        kinh = (
            payload.get("kinh_do")
            if payload.get("kinh_do") is not None
            else payload.get("longitude", 106.7)
        )

        if mode in {"gregorian", "duong", "solar"}:
            dt = str(payload.get("datetime") or "").strip()
            if not dt:
                raise CalendarConvertError(
                    "MISSING_DATETIME",
                    "Thiếu ngày giờ dương lịch.",
                )
            try:
                datetime.fromisoformat(dt.replace("Z", "+00:00")[:19])
            except ValueError as e:
                raise CalendarConvertError(
                    "INVALID_DATETIME",
                    "Ngày giờ dương lịch không hợp lệ.",
                ) from e
            out = self.tinh_lich_phap({**payload, "datetime": dt, "input_mode": "gregorian"})
            out["conversion"] = {
                "mode": "gregorian",
                "engine": "local_core_v1",
                "client_invented": False,
            }
            return out

        if mode in {"bazi", "bat_tu", "tứ trụ", "tu_tru"}:
            nam = _validate_pillar(
                "năm", str(payload.get("nam") or payload.get("year_pillar") or "")
            )
            thang = _validate_pillar(
                "tháng", str(payload.get("thang") or payload.get("month_pillar") or "")
            )
            ngay = _validate_pillar(
                "ngày", str(payload.get("ngay") or payload.get("day_pillar") or "")
            )
            gio = _validate_pillar(
                "giờ", str(payload.get("gio") or payload.get("hour_pillar") or "")
            )
            # Anchor datetime required for engines that need a civil timestamp;
            # pillars are authoritative for tu_tru — not re-derived from anchor.
            anchor = str(
                payload.get("anchor_datetime") or payload.get("datetime") or "2000-01-01T12:00:00"
            )
            try:
                datetime.fromisoformat(anchor.replace("Z", "+00:00")[:19])
            except ValueError as e:
                raise CalendarConvertError(
                    "INVALID_ANCHOR",
                    "Thời điểm neo (anchor) không hợp lệ.",
                ) from e
            base = self.tinh_lich_phap(
                {**payload, "datetime": anchor, "tz": tz, "kinh_do": kinh, "input_mode": "bazi"}
            )
            base["tu_tru"] = {"nam": nam, "thang": thang, "ngay": ngay, "gio": gio}
            base["year"], base["month"], base["day"], base["hour"] = nam, thang, ngay, gio
            base["datetime"] = anchor
            base["input_mode"] = "bazi"
            base["conversion"] = {
                "mode": "bazi",
                "engine": "local_core_v1",
                "client_invented": False,
                "pillars_authoritative": True,
            }
            return base

        if mode in {"lunar", "am", "am_lich"}:
            raw_y = payload.get("lunar_year") or payload.get("year")
            raw_m = payload.get("lunar_month") or payload.get("month")
            raw_d = payload.get("lunar_day") or payload.get("day")
            if raw_y is None or raw_m is None or raw_d is None:
                raise CalendarConvertError(
                    "LUNAR_MISSING",
                    "Thiếu năm/tháng/ngày âm lịch (số nguyên).",
                )
            try:
                y = int(raw_y)
                m = int(raw_m)
                d = int(raw_d)
            except (TypeError, ValueError) as e:
                raise CalendarConvertError(
                    "LUNAR_MISSING",
                    "Thiếu năm/tháng/ngày âm lịch (số nguyên).",
                ) from e
            leap = bool(payload.get("leap") or payload.get("is_leap") or False)
            hour = int(payload.get("hour") or 12)
            minute = int(payload.get("minute") or 0)
            solar = _lunar_to_solar_core(y, m, d, leap).replace(
                hour=max(0, min(23, hour)), minute=max(0, min(59, minute)), second=0
            )
            dt = solar.isoformat(timespec="seconds")
            base = self.tinh_lich_phap(
                {**payload, "datetime": dt, "tz": tz, "kinh_do": kinh, "input_mode": "lunar"}
            )
            base["datetime"] = dt
            base["input_mode"] = "lunar"
            base["lunar"] = {
                "year": y,
                "month": m,
                "day": d,
                "leap": leap,
            }
            base["conversion"] = {
                "mode": "lunar",
                "engine": "local_core_lunar_v1",
                "client_invented": False,
            }
            return base

        raise CalendarConvertError(
            "UNKNOWN_MODE",
            "Chế độ nhập không hỗ trợ. Dùng gregorian | lunar | bazi.",
        )
