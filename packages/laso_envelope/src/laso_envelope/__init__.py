"""laso_envelope - Pydantic models for the Tam Thuc la so envelope contract (PLAT-002).

See docs/contracts/laso-envelope.schema.json for the authoritative shape.
Engines (Rust) produce; Python AI/RAG layers consume read-only.
"""

from .models import (
    SUPPORTED_ENVELOPE_VERSIONS,
    CachCuc,
    DauVao,
    He,
    LaSo,
    Polarity,
    Provenance,
    attach_cache_key,
    cache_key,
    require_supported_version,
)

__all__ = [
    "SUPPORTED_ENVELOPE_VERSIONS",
    "CachCuc",
    "DauVao",
    "He",
    "LaSo",
    "Polarity",
    "Provenance",
    "attach_cache_key",
    "cache_key",
    "require_supported_version",
]
