from __future__ import annotations

from collections.abc import Iterable, Iterator

from tamthuc_kb.corpus.models import ClassicalSource, ClassicalUnit


class InMemoryCorpusStore:
    def __init__(self) -> None:
        self._sources: dict[str, ClassicalSource] = {}
        self._units: dict[str, ClassicalUnit] = {}
        self._by_citation: dict[str, str] = {}
        self._by_source: dict[str, list[str]] = {}

    def upsert_sources(self, sources: Iterable[ClassicalSource]) -> None:
        for s in sources:
            self._sources[s.source_id] = s
            self._by_source.setdefault(s.source_id, [])

    def upsert_units(self, units: Iterable[ClassicalUnit]) -> None:
        for u in units:
            if u.citation_id in self._by_citation and self._by_citation[u.citation_id] != u.unit_id:
                raise ValueError(f"duplicate citation_id: {u.citation_id}")
            existing = self._units.get(u.unit_id)
            if existing and existing.citation_id != u.citation_id:
                # re-bind
                self._by_citation.pop(existing.citation_id, None)
            self._units[u.unit_id] = u
            self._by_citation[u.citation_id] = u.unit_id
            ids = self._by_source.setdefault(u.source_id, [])
            if u.unit_id not in ids:
                ids.append(u.unit_id)

    def units_of_source(self, source_id: str) -> list[ClassicalUnit]:
        ids = self._by_source.get(source_id, [])
        units = [self._units[i] for i in ids if i in self._units]
        return sorted(units, key=lambda u: u.ordinal)

    def get_unit(self, unit_id: str) -> ClassicalUnit | None:
        return self._units.get(unit_id)

    def resolve_citation(self, citation_id: str) -> ClassicalUnit | None:
        uid = self._by_citation.get(citation_id)
        return self._units.get(uid) if uid else None

    def iter_units(self) -> Iterator[ClassicalUnit]:
        yield from self._units.values()

    def source_count(self) -> int:
        return len(self._sources)

    def unit_count(self) -> int:
        return len(self._units)

    def dangling_citations(self, referenced: Iterable[str]) -> list[str]:
        return [c for c in referenced if c not in self._by_citation]
