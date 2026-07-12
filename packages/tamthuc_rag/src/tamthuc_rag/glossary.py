"""Curated classical term glossary — FR-RAG-005."""

from __future__ import annotations

import json
from enum import StrEnum
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

System = Literal["qimen", "liuren", "taiyi", "all"]


class SenseLayer(StrEnum):
    ban_nghia = "ban_nghia"
    dan_than = "dan_than"
    gia_ta = "gia_ta"
    dien_tich = "dien_tich"


class TermSense(BaseModel):
    model_config = ConfigDict(extra="forbid")
    layer: SenseLayer
    gloss: str
    surface_forms: list[str]
    weight: float
    reliable: bool = True
    citations: list[str] = Field(default_factory=list)


class TermEntry(BaseModel):
    model_config = ConfigDict(extra="forbid")
    term: str
    term_han: str | None = None
    system: System
    aliases: list[str] = Field(default_factory=list)
    senses: list[TermSense]


class TermGlossary:
    def __init__(self, entries: list[TermEntry]) -> None:
        self.entries = entries

    @classmethod
    def load(cls, paths: list[Path]) -> TermGlossary:
        entries: list[TermEntry] = []
        for p in paths:
            data = json.loads(Path(p).read_text(encoding="utf-8"))
            rows = data if isinstance(data, list) else data.get("terms", [])
            entries.extend(TermEntry.model_validate(r) for r in rows)
        return cls(entries)

    def match(self, query: str, system: System) -> list[TermEntry]:
        q = query.lower()
        out: list[TermEntry] = []
        for e in self.entries:
            if e.system not in (system, "all"):
                continue
            forms = [e.term, e.term_han or "", *e.aliases]
            if any(f and f.lower() in q for f in forms):
                out.append(e)
                continue
            # also match surface forms as detection cues
            for s in e.senses:
                if any(sf.lower() in q for sf in s.surface_forms if sf):
                    out.append(e)
                    break
        return out
