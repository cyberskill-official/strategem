"""Engine clients — TASK-API-001 / E2E cast path.

`LocalEngineClient` produces la so envelopes with ban shapes the web chart
consumes. It prefers an optional Rust cast CLI when `CAST_CLI` is set; otherwise
uses a deterministic local cast (same plate structure as cyberos-qimen envelope).

TT-022: cast-cli failures are logged + metered; production with
READY_REQUIRE_CAST_CLI fail-closes instead of silent local fallback.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Protocol
from uuid import uuid4

from tamthuc_api.observability.logging import structured_log

log = logging.getLogger("tamthuc_api.clients.engine")

_ENGINE_CODE = {
    "qimen": "qmdg",
    "liuren": "ln",
    "taiyi": "tat",
    "ky_mon": "qmdg",
    "luc_nham": "ln",
    "thai_at": "tat",
}


class EngineClient(Protocol):
    def cast(self, system: str, lich_phap: dict[str, Any]) -> dict[str, Any]: ...


class CastCliRequiredError(RuntimeError):
    """Raised when cast-cli is required but failed or missing (fail-closed)."""

    code = "CAST_CLI_REQUIRED"

    def __init__(self, message: str = "cast-cli required") -> None:
        self.message = message
        super().__init__(message)


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


def _engine_code(system: str) -> str:
    return _ENGINE_CODE.get(system, system if system in {"qmdg", "ln", "tat", "core"} else "core")


def _require_cast_cli_strict() -> bool:
    """Fail closed when READY_REQUIRE_CAST_CLI and prod-like (or always when flag set)."""
    flag = os.environ.get("READY_REQUIRE_CAST_CLI", "").strip().lower() in {
        "1",
        "true",
        "yes",
    }
    if not flag:
        return False
    app_env = (os.environ.get("APP_ENV") or os.environ.get("ENV") or "").lower()
    # Flag alone is enough in staging/prod compose; also honour explicit prod envs.
    if app_env in {"production", "prod", "staging"}:
        return True
    # READY_REQUIRE_CAST_CLI=1 without ENV still fail-closes cast path (readiness already 503).
    return flag


def _stamp_provenance(
    envelope: dict[str, Any],
    *,
    system: str,
    engine_source: str,
    engine_version: str | None = None,
) -> dict[str, Any]:
    prov = dict(envelope.get("provenance") or {})
    prov["engine"] = _engine_code(system)
    if engine_version:
        prov["engine_version"] = engine_version
    prov.setdefault("cast_at", datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"))
    prov["engine_source"] = engine_source
    envelope["provenance"] = prov
    return envelope


class StubEngineClient:
    """Minimal stub (tests that only check call sequence)."""

    def cast(self, system: str, lich_phap: dict[str, Any]) -> dict[str, Any]:
        he = {"qimen": "ky_mon", "liuren": "luc_nham", "taiyi": "thai_at"}.get(system, system)
        lp = dict(lich_phap)
        lp.setdefault(
            "co_lich_phap",
            {"stamped": True, "source": "stub", "tz": lp.get("tz", "+07:00")},
        )
        out: dict[str, Any] = {
            "envelope_version": 1,
            "he": he,
            "lich_phap": lp,
            "ban": {"stub": True},
            "cach_cuc": [],
            "co_truong_phai": lp.get("co_truong_phai") or {"stamped": "default", "source": "stub"},
            "dau_vao": {},
            "provenance": {
                "engine": _engine_code(system),
                "engine_version": "0.1.0",
                "cast_at": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
            },
        }
        return _stamp_provenance(out, system=system, engine_source="stub")


def probe_cast_cli(cast_cli: str | None = None) -> dict[str, Any]:
    """Readiness probe for CAST_CLI (configured path + executable)."""
    path = cast_cli if cast_cli is not None else os.environ.get("CAST_CLI")
    configured = bool(path and str(path).strip())
    present = False
    if configured and path is not None:
        p = Path(path).expanduser()
        present = p.is_file() and os.access(p, os.X_OK)
    mode = "cast_cli" if present else "local_fallback"
    return {
        "cast_cli_configured": configured,
        "cast_cli_present": present,
        "cast_cli_path": path if configured else None,
        "engine_mode": mode,
    }


class LocalEngineClient:
    """Deterministic local cast with chart-ready ban; optional CAST_CLI."""

    def __init__(
        self,
        cast_cli: str | None = None,
        *,
        metrics: Any | None = None,
    ) -> None:
        self.cast_cli = cast_cli or os.environ.get("CAST_CLI")
        self.metrics = metrics
        self.last_engine_source: str = "local_fallback"

    def cast(self, system: str, lich_phap: dict[str, Any]) -> dict[str, Any]:
        if self.cast_cli:
            try:
                out = self._cast_via_cli(system, lich_phap)
                self.last_engine_source = "cast_cli"
                return _stamp_provenance(out, system=system, engine_source="cast_cli")
            except (OSError, subprocess.SubprocessError, json.JSONDecodeError, KeyError) as exc:
                reason = type(exc).__name__
                log.warning(
                    structured_log(
                        "cast_cli.fallback",
                        request_id=str(uuid4()),
                        system=system,
                        reason=reason,
                        cast_cli=str(self.cast_cli),
                    )
                )
                if self.metrics is not None:
                    self.metrics.record_cast_fallback(system=system, reason=reason)
                if _require_cast_cli_strict():
                    raise CastCliRequiredError(f"cast-cli required but failed: {reason}") from exc
        out = self._cast_local(system, lich_phap)
        self.last_engine_source = "local_fallback"
        return out

    def _cast_via_cli(self, system: str, lich_phap: dict[str, Any]) -> dict[str, Any]:
        assert self.cast_cli is not None
        payload = json.dumps({"system": system, "lich_phap": lich_phap}, default=str)
        # cast-cli reads stdin JSON; argv is optional
        cmd = [self.cast_cli]
        proc = subprocess.run(
            cmd,
            input=payload,
            text=True,
            capture_output=True,
            check=True,
            timeout=30,
        )
        out: dict[str, Any] = json.loads(proc.stdout)
        if "envelope_version" not in out and "he" not in out:
            raise KeyError("cast-cli output missing envelope fields")
        # COV-002: stamp school + calendar flags if CLI omitted them
        ctp = lich_phap.get("co_truong_phai")
        if ctp and not out.get("co_truong_phai"):
            out["co_truong_phai"] = ctp
        if not out.get("co_truong_phai"):
            out["co_truong_phai"] = {"stamped": "default", "source": "cast_cli_client"}
        lp = out.get("lich_phap")
        if not isinstance(lp, dict):
            lp = {}
            out["lich_phap"] = lp
        if "co_lich_phap" not in lp or not lp.get("co_lich_phap"):
            lp["co_lich_phap"] = lich_phap.get("co_lich_phap") or {
                "tz": lich_phap.get("tz", "+07:00"),
                "longitude": lich_phap.get("kinh_do") or lich_phap.get("longitude") or 106.7,
                "stamped": True,
                "source": "cast_cli_client",
            }
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
            # Shape matches cyberos-luchnham envelope ban (TASK-LN-006 / TASK-CHART-002)
            chi12 = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
            offset = seed % 12
            dia = list(chi12)
            thien = chi12[offset:] + chi12[:offset]
            nt, gc = chi12[offset], chi12[seed % 12]
            generals = [
                "BachHo",
                "ThienKhong",
                "ThanhLong",
                "CauTran",
                "LucHop",
                "ChuTuoc",
                "DangXa",
                "QuyNhan",
                "ThienHau",
                "ThaiAm",
                "HuyenVu",
                "ThaiThuong",
            ]
            generals = _rot(generals, seed % 12)
            ban = {
                "nguyet_tuong": nt,
                "gio_chiem": gc,
                "thien_dia_ban": {
                    "dia": dia,
                    "thien": thien,
                    "nguyet_tuong": nt,
                    "gio_chiem": gc,
                    "state": "PhucNgam"
                    if offset == 0
                    else ("PhanNgam" if offset == 6 else "Thuong"),
                },
                "tu_khoa": [
                    [thien[0], dia[0]],
                    [thien[1], dia[1]],
                    [thien[2], dia[2]],
                    [thien[3], dia[3]],
                ],
                "tam_truyen": {
                    "so": thien[0],
                    "trung": thien[1],
                    "mat": thien[2],
                    "phap": "PhucNgam" if offset == 0 else "Thuong",
                },
                "thien_tuong": generals,
                "khoa_the": ["PhucNgam" if offset == 0 else "Thuong"],
            }
            cach_cuc = [
                {
                    "id": "PhucNgam" if offset == 0 else "liuren_thuong",
                    "name": "伏吟" if offset == 0 else "元胎",
                    "cung": None,
                    "polarity": "trung",
                    "score": 0.6,
                    "citations": ["ln_nguyen_thai_1"],
                }
            ]
        else:
            # Tai Yi shape (TASK-CHART-003)
            thai_cung = (seed % 8) + 1  # 1..9 skip 5 often
            if thai_cung == 5:
                thai_cung = 3
            ban = {
                "thai_at_cung": thai_cung,
                "thai_at_ring": seed % 16,
                "thap_luc_than": [
                    {
                        "ring": i,
                        "chi": [
                            "子",
                            "丑",
                            "寅",
                            "卯",
                            "辰",
                            "巳",
                            "午",
                            "未",
                            "申",
                            "酉",
                            "戌",
                            "亥",
                            "子",
                            "丑",
                            "寅",
                            "卯",
                        ][i],
                        "han": [
                            "地主",
                            "陽德",
                            "和德",
                            "呂申",
                            "高叢",
                            "太陽",
                            "大炅",
                            "大神",
                            "大威",
                            "天道",
                            "大武",
                            "武德",
                            "太簇",
                            "陰主",
                            "陰德",
                            "大義",
                        ][i],
                        "loai": "gian_than" if i % 2 else "chinh_cung",
                    }
                    for i in range(16)
                ],
                "bat_tuong": {
                    "chu_dai_tuong": (seed % 9) + 1,
                    "chu_tham_tuong": ((seed + 2) % 9) + 1,
                    "khach_dai_tuong": ((seed + 4) % 9) + 1,
                    "khach_tham_tuong": ((seed + 5) % 9) + 1,
                    "ke_than": seed % 9,
                    "thuy_kich": (seed + 1) % 9,
                    "van_xuong": (seed + 3) % 9 + 1,
                },
                "cac_toan": {
                    "chu_toan": 20 + (seed % 30),
                    "khach_toan": 30 + (seed % 40),
                    "chu_truong_doan": "truong" if seed % 2 == 0 else "doan",
                    "khach_truong_doan": "truong" if seed % 3 else "doan",
                },
            }
            cach_cuc = [
                {
                    "id": "tat_yem",
                    "name": "掩",
                    "cung": thai_cung,
                    "polarity": "trung",
                    "score": 0.5,
                    "citations": ["kim_kinh_thuc_kinh"],
                }
            ]

        # COV-002: always stamp full school + calendar flags (no silent omit)
        co_truong = dict(lich_phap.get("co_truong_phai") or {})
        if not co_truong:
            co_truong = {"stamped": "default", "source": "local_engine"}
        co_lich = dict(lich_phap.get("co_lich_phap") or {})
        if not co_lich:
            co_lich = {
                "tz": str(lich_phap.get("tz") or dau_vao.get("tz") or "+07:00"),
                "longitude": lich_phap.get("kinh_do", dau_vao.get("kinh_do", 106.7)),
                "stamped": True,
                "source": "local_engine",
            }
        lich_out = dict(lich_phap)
        lich_out["co_lich_phap"] = co_lich

        out = {
            "envelope_version": 1,
            "he": he,
            "dau_vao": dau_vao,
            "lich_phap": lich_out,
            "ban": ban,
            "cach_cuc": cach_cuc,
            "co_truong_phai": co_truong,
            "provenance": {
                "engine": _engine_code(system),
                "engine_version": "local-0.1.0",
                "cast_at": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "cache_key": hashlib.sha256(
                    json.dumps({"s": system, "l": lich_out}, sort_keys=True, default=str).encode()
                ).hexdigest(),
            },
        }
        return _stamp_provenance(
            out,
            system=system,
            engine_source="local_fallback",
            engine_version="local-0.1.0",
        )


def resolve_cast_cli() -> str | None:
    """Resolve CAST_CLI path: env, or cargo target debug/release binary."""
    env = os.environ.get("CAST_CLI")
    if env and Path(env).exists():
        return env
    # monorepo defaults (dev)
    root = Path(__file__).resolve()
    for _ in range(8):
        root = root.parent
        candidates = [
            root / "target" / "release" / "cast-cli",
            root / "target" / "debug" / "cast-cli",
        ]
        for c in candidates:
            if c.exists():
                return str(c)
        if (root / "Cargo.toml").exists() and (root / "crates" / "cast-cli").exists():
            break
    return None


def default_engine(*, metrics: Any | None = None) -> EngineClient:
    """Prefer CAST_CLI (or discovered cast-cli binary), else local deterministic engine."""
    cli = resolve_cast_cli()
    return LocalEngineClient(cli, metrics=metrics)
