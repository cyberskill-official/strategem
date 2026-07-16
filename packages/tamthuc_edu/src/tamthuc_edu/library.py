"""Bilingual classical library browser — TASK-EDU-003."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class LibraryEntry(BaseModel):
    model_config = ConfigDict(extra="forbid")
    unit_id: str
    title: str
    han: str = ""
    bach_thoai: str = ""
    dich: str = ""
    system: str = "all"


class ClassicalLibrary:
    def __init__(self, entries: list[LibraryEntry] | None = None) -> None:
        self.entries = entries or []

    def search(self, q: str, *, lang: str = "all") -> list[LibraryEntry]:
        ql = q.lower()
        out: list[LibraryEntry] = []
        for e in self.entries:
            blob = f"{e.title} {e.han} {e.bach_thoai} {e.dich}".lower()
            if ql in blob:
                if lang == "han" and not e.han:
                    continue
                if lang == "vi" and not e.bach_thoai:
                    continue
                if lang == "en" and not e.dich:
                    continue
                out.append(e)
        return out
