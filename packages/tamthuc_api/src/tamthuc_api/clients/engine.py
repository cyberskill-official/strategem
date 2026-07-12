"""Engine clients — FR-API-001 / E2E cast path.

`LocalEngineClient` produces la so envelopes with ban shapes the web chart
consumes. It prefers an optional Rust cast CLI when `CAST_CLI` is set; otherwise
uses a deterministic local cast (same plate structure as cyberos-qimen envelope).
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
from pathlib import Path
from typing import Any, Protocol


class EngineClient(Protocol):
    def cast(self, system: str, lich_phap: dict[str, Any]) -> dict[str, Any]: ...


_STEMS = ["戊", "己", "庚", "辛", "壬", "癸", "丁", "丙", "乙"]
_DOORS = ["Huu", "Tu", "Thuong", "Do", None, "Khai", "Kinh", "Sinh", "Canh"]
_STARS = [
    "ThienBong",
    "ThienNham",
    "ThienXung",
    "ThienPhu",
    "ThienAnh",
    "ThienCam",
    "ThienTru",
    "ThienTam",
    "ThienTruc",
]
_GODS = [
    "TrucPhu",
    "TangXa",
    "ThaiAm",
    "LucHop",
    "BachHo",
    "HuyenVu",
    "CuuDia",
    "CuuThien",
    None,
]


def _rot(seq: list[Any], n: int) -> list[Any]:
    n = n % len(seq)
    return seq[n:] + seq[:n]


def _seed_int(payload: dict[str, Any]) -> int:
    raw = json.dumps(payload, sort_keys=True, default=str).encode("utf-8")
    return int(hashlib.sha256(raw).hexdigest()[:8], 16)


class StubEngineClient:
    """Minimal stub (tests that only check call sequence)."""

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


class LocalEngineClient:
    """Deterministic local cast with chart-ready ban; optional CAST_CLI."""

    def __init__(self, cast_cli: str | None = None) -> None:
        self.cast_cli = cast_cli or os.environ.get("CAST_CLI")

    def cast(self, system: str, lich_phap: dict[str, Any]) -> dict[str, Any]:
        if self.cast_cli:
            try:
                return self._cast_via_cli(system, lich_phap)
            except (OSError, subprocess.SubprocessError, json.JSONDecodeError, KeyError):
                pass
        return self._cast_local(system, lich_phap)

    def _cast_via_cli(self, system: str, lich_phap: dict[str, Any]) -> dict[str, Any]:
        assert self.cast_cli is not None
        payload = json.dumps({"system": system, "lich_phap": lich_phap})
        proc = subprocess.run(
            [self.cast_cli, "cast"],
            input=payload,
            text=True,
            capture_output=True,
            check=True,
            timeout=30,
        )
        out: dict[str, Any] = json.loads(proc.stdout)
        return out

    def _cast_local(self, system: str, lich_phap: dict[str, Any]) -> dict[str, Any]:
        he = {"qimen": "ky_mon", "liuren": "luc_nham", "taiyi": "thai_at"}.get(system, system)
        seed = _seed_int({"system": system, "lich": lich_phap})
        dau_vao = {
            "datetime": lich_phap.get("datetime") or lich_phap.get("dt") or "",
            "tz": lich_phap.get("tz", "+07:00"),
            "kinh_do": lich_phap.get("kinh_do") or lich_phap.get("longitude") or 106.7,
            "loai_cau_hoi": lich_phap.get("question_type")
            or lich_phap.get("loai_cau_hoi")
            or "trach_thoi",
        }
        if system == "qimen" or he == "ky_mon":
            ban = {
                "dinh_cuc": {
                    "so_cuc": (seed % 9) + 1,
                    "duong_don": seed % 2 == 0,
                    "nguyen": ["thuong", "trung", "ha"][seed % 3],
                },
                "dia_ban": _rot(_STEMS, seed % 9),
                "thien_ban": _rot(_STEMS, (seed // 3) % 9),
                "cuu_tinh": _rot(_STARS, seed % 9),
                "bat_mon": _rot(list(_DOORS), seed % 9),
                "bat_than": _rot(list(_GODS), (seed // 5) % 9),
                "truc_phu": seed % 9,
                "truc_su": (seed // 2) % 9,
            }
            cach_cuc = [
                {
                    "id": "qimen_thanh_long_hoi_dau",
                    "name": "青龍返首",
                    "cung": (seed % 9) + 1,
                    "polarity": "cat",
                    "score": 0.85,
                    "citations": ["yba_khac_ung_1", "kmdg_cach_cuc"],
                }
            ]
            if seed % 3 == 0:
                cach_cuc.append(
                    {
                        "id": "qimen_bai_ho_cuong_su",
                        "name": "白虎猖狂",
                        "cung": ((seed + 3) % 9) + 1,
                        "polarity": "hung",
                        "score": 0.7,
                        "citations": ["kmdg_cach_cuc"],
                    }
                )
        elif system == "liuren" or he == "luc_nham":
            ban = {
                "thien_ban": _rot(_STEMS, seed % 9)[:4],
                "dia_ban": _rot(_STEMS, (seed + 1) % 9)[:4],
                "tam_truyen": [
                    {"than": "青龍", "chi": "子"},
                    {"than": "六合", "chi": "丑"},
                    {"than": "太常", "chi": "寅"},
                ],
            }
            cach_cuc = [
                {
                    "id": "liuren_nguyen_thai",
                    "name": "元胎",
                    "cung": None,
                    "polarity": "trung",
                    "score": 0.6,
                    "citations": ["ln_nguyen_thai_1"],
                }
            ]
        else:
            ban = {
                "thai_at_ring": seed % 16,
                "cuu_cung": list(range(1, 10)),
            }
            cach_cuc = [
                {
                    "id": "tat_yem",
                    "name": "掩",
                    "cung": seed % 9,
                    "polarity": "trung",
                    "score": 0.5,
                    "citations": ["kim_kinh_thuc_kinh"],
                }
            ]

        return {
            "envelope_version": 1,
            "he": he,
            "dau_vao": dau_vao,
            "lich_phap": lich_phap,
            "ban": ban,
            "cach_cuc": cach_cuc,
            "co_truong_phai": lich_phap.get("co_truong_phai") or {},
            "provenance": {
                "engine": system,
                "engine_version": "local-0.1.0",
                "cache_key": hashlib.sha256(
                    json.dumps({"s": system, "l": lich_phap}, sort_keys=True, default=str).encode()
                ).hexdigest()[:16],
            },
        }


def default_engine() -> EngineClient:
    """Prefer CAST_CLI, else local deterministic engine."""
    cli = os.environ.get("CAST_CLI")
    if cli and Path(cli).exists():
        return LocalEngineClient(cli)
    return LocalEngineClient()
