from __future__ import annotations

from typing import Any

from tamthuc_kb.corpus.models import ClassicalSource, ClassicalUnit, LayerText, UnitType


def segment_source(source: ClassicalSource, raw_units: list[dict[str, Any]]) -> list[ClassicalUnit]:
    """Validate natural-unit segmentation: monotonic ordinal, citation under prefix."""
    out: list[ClassicalUnit] = []
    prev_ord = -1
    for raw in raw_units:
        ordinal = int(raw["ordinal"])
        if ordinal <= prev_ord:
            raise ValueError(f"ordinal must be strictly increasing; got {ordinal} after {prev_ord}")
        prev_ord = ordinal
        ut = UnitType(str(raw["unit_type"]))
        citation = str(raw["citation_id"])
        if not citation.startswith(source.citation_prefix):
            raise ValueError(f"citation_id {citation} must start with {source.citation_prefix}")
        layers = LayerText(
            nguyen_van_han=_opt_str(raw.get("nguyen_van_han")),
            bach_thoai=_opt_str(raw.get("bach_thoai")),
            dich=_opt_str(raw.get("dich")),
        )
        unit = ClassicalUnit(
            unit_id=str(raw.get("unit_id") or f"{source.source_id}:{ordinal}"),
            source_id=source.source_id,
            citation_id=citation,
            unit_type=ut,
            ordinal=ordinal,
            system=source.system,
            layers=layers,
        )
        out.append(unit)
    return out


def _opt_str(v: Any) -> str | None:
    if v is None:
        return None
    return str(v)
