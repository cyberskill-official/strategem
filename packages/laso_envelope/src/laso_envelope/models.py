"""Pydantic models matching docs/contracts/laso-envelope.schema.json and Rust laso-envelope.

extra="forbid" on root and sub-models (except opaque ban/lich_phap where noted).
Cache key computation must be bit-compatible in spirit with the Rust sha256 canonical form.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime
from enum import StrEnum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class He(StrEnum):
    luc_nham = "luc_nham"
    ky_mon = "ky_mon"
    thai_at = "thai_at"


class Polarity(StrEnum):
    cat = "cat"
    hung = "hung"
    trung = "trung"


class CachCuc(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str
    name: str
    cung: int | None = None
    polarity: Polarity
    score: float | None = Field(default=None, ge=0.0, le=1.0)
    citations: list[str] = Field(default_factory=list)


class DauVao(BaseModel):
    model_config = ConfigDict(extra="forbid")
    datetime: str
    tz: str = Field(pattern=r"^[+-]\d{2}:\d{2}$")
    kinh_do: float = Field(ge=-180.0, le=180.0)
    loai_cau_hoi: str | None = None


class Provenance(BaseModel):
    model_config = ConfigDict(extra="forbid")
    engine: Literal["qmdg", "ln", "tat", "core"]
    engine_version: str
    cast_at: datetime
    cache_key: str | None = None


class LaSo(BaseModel):
    """Root envelope. Matches the JSON Schema and Rust struct exactly (for v1).

    - ban and lich_phap are left as dict (opaque but present) to avoid tight coupling.
    - co_truong_phai must be a dict of str->str; keys are sorted for stable hashing.
    """

    model_config = ConfigDict(extra="forbid")

    envelope_version: int = Field(ge=1)
    he: He
    dau_vao: DauVao
    lich_phap: dict[str, Any]  # CORE output; full shape owned by CORE-005
    ban: dict[str, Any]  # engine-specific; opaque at envelope
    cach_cuc: list[CachCuc] = Field(default_factory=list)
    co_truong_phai: dict[str, str]
    provenance: Provenance


SUPPORTED_ENVELOPE_VERSIONS: frozenset[int] = frozenset({1})
"""Envelope versions this build understands. Single source of truth for
require_supported_version() (and the intended range of LaSo.envelope_version)."""


def require_supported_version(la: LaSo) -> None:
    """Raise if version not supported. Mirrors Rust behavior."""
    if la.envelope_version not in SUPPORTED_ENVELOPE_VERSIONS:
        raise ValueError(
            f"unsupported envelope version: {la.envelope_version} "
            f"(supported: {sorted(SUPPORTED_ENVELOPE_VERSIONS)})"
        )


def cache_key(la: LaSo) -> str:
    """Stable cache key.

    Must produce identical value (for same logical input) as the Rust implementation.
    We canonicalize by sorting the co_truong_phai keys and using a deterministic
    subset (he + dau_vao + sorted co_truong_phai + lich_phap).
    """
    canon: dict[str, Any] = {
        "he": la.he.value,
        "dau_vao": la.dau_vao.model_dump(),
        "co_truong_phai": dict(sorted(la.co_truong_phai.items())),
        "lich_phap": la.lich_phap,
    }
    blob = json.dumps(canon, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def attach_cache_key(la: LaSo) -> LaSo:
    """Return a copy with provenance.cache_key set (pure)."""
    key = cache_key(la)
    p = la.provenance.model_copy(update={"cache_key": key})
    return la.model_copy(update={"provenance": p})
