"""Citation collection along graph paths — TASK-KB-005."""

from __future__ import annotations

from typing import Any, Protocol


class ClassicalStore(Protocol):
    def resolve_citation(self, citation_id: str) -> object | None: ...


class NullClassicalStore:
    def resolve_citation(self, citation_id: str) -> object | None:
        return {"id": citation_id}  # accept all in tests unless overridden


class FilteringClassicalStore:
    def __init__(self, known: set[str]) -> None:
        self.known = known

    def resolve_citation(self, citation_id: str) -> object | None:
        return {"id": citation_id} if citation_id in self.known else None


def collect_path_citations(
    path_nodes: list[Any],
    path_edges: list[Any],
) -> list[str]:
    """De-dupe citations from cach_cuc/than_sat nodes and edge attrs."""
    out: list[str] = []
    seen: set[str] = set()
    for n in path_nodes:
        kind = getattr(n, "kind", None)
        kind_v = str(kind.value) if kind is not None and hasattr(kind, "value") else str(kind or "")
        if kind_v in ("cach_cuc", "than_sat"):
            for c in (n.attrs or {}).get("citations") or []:
                cid = str(c)
                if cid not in seen:
                    seen.add(cid)
                    out.append(cid)
        for c in (n.attrs or {}).get("citations") or []:
            cid = str(c)
            if cid not in seen:
                seen.add(cid)
                out.append(cid)
    for e in path_edges:
        attrs = getattr(e, "attrs", {}) or {}
        for c in attrs.get("citations") or []:
            cid = str(c)
            if cid not in seen:
                seen.add(cid)
                out.append(cid)
    return out


def resolvable(citation_ids: list[str], corpus: ClassicalStore) -> tuple[list[str], list[str]]:
    ok: list[str] = []
    dangling: list[str] = []
    for cid in citation_ids:
        if corpus.resolve_citation(cid) is None:
            dangling.append(cid)
        else:
            ok.append(cid)
    return ok, dangling
