"""Knowledge API — COV-019 pattern library + COV-022 graph neighbors."""

from __future__ import annotations

from functools import lru_cache
from typing import Any

from fastapi import APIRouter, Query

router = APIRouter(tags=["knowledge"])

_PROPHECY_BLOCK = (
    "prophecy",
    "fortune-telling",
    "destined",
    "guaranteed fate",
    "bói toán chắc chắn",
    "định mệnh chắc",
)


def _load_patterns() -> list[dict[str, Any]]:
    try:
        from tamthuc_kb.seed.loader import load_all_patterns

        rows = load_all_patterns()
        out: list[dict[str, Any]] = []
        for r in rows:
            if not isinstance(r, dict):
                continue
            modern = str(r.get("meaning_modern") or "")
            classical = str(r.get("meaning_classical") or "")
            blob = (modern + " " + classical).lower()
            if any(b in blob for b in _PROPHECY_BLOCK):
                # strip prophecy wording for product surface
                modern = "Educational classical pattern note (see citations)."
            out.append(
                {
                    "id": r.get("id"),
                    "system": r.get("system"),
                    "he": {
                        "qimen": "ky_mon",
                        "liuren": "luc_nham",
                        "taiyi": "thai_at",
                    }.get(str(r.get("system")), r.get("system")),
                    "name": r.get("name"),
                    "name_han": r.get("name_han") or r.get("name"),
                    "polarity": r.get("polarity"),
                    "meaning_modern": modern,
                    "meaning_classical": classical,
                    "citations": r.get("citations") or [],
                    "conditions": r.get("conditions"),
                    "status": r.get("status"),
                }
            )
        return out
    except Exception:
        return []


@router.get("/knowledge/patterns")
def list_patterns(
    he: str | None = Query(
        default=None,
        description="Alias of system: qimen|liuren|taiyi or Vietnamese he codes (ky_mon|luc_nham|thai_at)",
    ),
    system: str | None = Query(
        default=None,
        description="Canonical classical system filter: qimen|liuren|taiyi (TASK-API-001 / TASK-API-005)",
    ),
    q: str | None = Query(default=None, description="search name/gloss"),
    limit: int = Query(default=200, ge=1, le=500),
) -> dict[str, Any]:
    rows = _load_patterns()
    # Canonical filter is ?system=; he= remains a supported alias (TASK-API-005).
    he_n = (system or he or "").strip().lower()
    if he_n:
        alias = {
            "ky_mon": "qimen",
            "qimen": "qimen",
            "luc_nham": "liuren",
            "liuren": "liuren",
            "thai_at": "taiyi",
            "taiyi": "taiyi",
        }
        want = alias.get(he_n, he_n)
        rows = [r for r in rows if str(r.get("system")) == want or str(r.get("he")) == he_n]
    if q:
        ql = q.strip().lower()
        rows = [
            r
            for r in rows
            if ql in str(r.get("name") or "").lower()
            or ql in str(r.get("name_han") or "").lower()
            or ql in str(r.get("meaning_modern") or "").lower()
        ]
    return {
        "patterns": rows[:limit],
        "total": len(rows),
        "source": "tamthuc_kb.seed",
    }


@lru_cache(maxsize=1)
def _seeded_graph() -> Any:
    """COV-022: in-memory ngũ hành graph — only stored edges, never invented."""
    from tamthuc_kb.graph.seed import seed_ngu_hanh
    from tamthuc_kb.graph.store import InMemoryGraphStore

    store = InMemoryGraphStore()
    seed_ngu_hanh(store)
    return store


@router.get("/knowledge/graph/neighbors")
def graph_neighbors(
    node_id: str = Query(..., description="e.g. ngu_hanh_moc"),
    rel: str | None = Query(default=None, description="optional edge type filter: sinh|khac"),
    max_hops: int = Query(default=1, ge=1, le=3),
) -> dict[str, Any]:
    """COV-022: node neighbors from stored graph only."""
    try:
        store = _seeded_graph()
        from tamthuc_kb.graph.taxonomy import EdgeRel

        node = store.get_node(node_id)
        if node is None:
            return {
                "node_id": node_id,
                "neighbors": [],
                "found": False,
                "source": "stored_graph_only",
            }

        rel_enum = None
        if rel:
            try:
                rel_enum = EdgeRel(rel.strip().lower())
            except Exception:
                rel_enum = None

        edges = store.neighbors(node_id, rel=rel_enum)
        neighbors: list[dict[str, Any]] = []
        for e in edges:
            erel_s = e.rel.value if hasattr(e.rel, "value") else str(e.rel)
            if e.src == node_id:
                neighbors.append(
                    {"node_id": e.dst, "rel": erel_s, "direction": "out", "label": e.dst}
                )
            elif e.dst == node_id and max_hops >= 1:
                neighbors.append(
                    {"node_id": e.src, "rel": erel_s, "direction": "in", "label": e.src}
                )
        return {
            "node_id": node_id,
            "neighbors": neighbors,
            "found": True,
            "source": "stored_graph_only",
            "note": "Edges come only from seed/store — never invented at query time.",
        }
    except Exception as e:
        return {
            "node_id": node_id,
            "neighbors": [],
            "found": False,
            "error": str(e),
            "source": "stored_graph_only",
        }


@router.get("/knowledge/graph/nodes")
def graph_nodes() -> dict[str, Any]:
    """List seeded graph nodes for explorer UI."""
    try:
        store = _seeded_graph()
        items = [
            {
                "id": n.id,
                "label": n.label,
                "kind": str(getattr(n.kind, "value", n.kind)),
            }
            for n in store.nodes.values()
        ]
        return {"nodes": items, "source": "stored_graph_only"}
    except Exception as e:
        return {"nodes": [], "error": str(e)}
