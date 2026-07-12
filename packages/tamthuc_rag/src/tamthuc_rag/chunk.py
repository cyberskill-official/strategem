from __future__ import annotations

from tamthuc_rag.models import Chunk, Layer, UnitRecord


def chunks_for_unit(unit: UnitRecord, *, model: str, dim: int) -> list[Chunk]:
    layers: list[tuple[Layer, str | None]] = [
        ("han", unit.nguyen_van_han),
        ("bach_thoai", unit.bach_thoai),
        ("dich", unit.dich),
    ]
    out: list[Chunk] = []
    for layer, text in layers:
        if text and text.strip():
            out.append(
                Chunk(
                    chunk_id=f"{unit.unit_id}:{layer}:{model}",
                    unit_id=unit.unit_id,
                    layer=layer,
                    text=text.strip(),
                    system=unit.system,
                    unit_type=unit.unit_type,
                    citation_id=unit.citation_id,
                    model=model,
                    dim=dim,
                )
            )
    return out
