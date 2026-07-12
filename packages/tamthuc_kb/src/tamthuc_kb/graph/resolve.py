"""Seed token → graph node resolution — FR-KB-005."""

from __future__ import annotations

from typing import Literal

from tamthuc_kb.graph.store import GraphStore

System = Literal["qimen", "liuren", "taiyi", "all"]


def resolve_seeds(
    tokens: list[str],
    system: System,
    store: GraphStore,
) -> tuple[list[str], list[str]]:
    """Map tokens to node ids (Han / romanized / slug / id). Never guess."""
    resolved: list[str] = []
    unresolved: list[str] = []
    # index aliases
    alias_index: dict[str, str] = {}
    for nid, node in getattr(store, "nodes", {}).items() if hasattr(store, "nodes") else []:
        alias_index[nid.lower()] = nid
        if node.label:
            alias_index[node.label.lower()] = nid
        han = str(node.attrs.get("han") or node.attrs.get("label_han") or "")
        if han:
            alias_index[han.lower()] = nid
        for a in node.attrs.get("aliases") or []:
            alias_index[str(a).lower()] = nid
        slug = str(node.attrs.get("slug") or "")
        if slug:
            alias_index[slug.lower()] = nid

    # also walk via get if store has no .nodes
    if not alias_index and hasattr(store, "nodes_by_kind"):
        from tamthuc_kb.graph.taxonomy import NodeKind

        for kind in NodeKind:
            for node in store.nodes_by_kind(kind):
                alias_index[node.id.lower()] = node.id
                if node.label:
                    alias_index[node.label.lower()] = node.id
                han = str(node.attrs.get("han") or "")
                if han:
                    alias_index[han.lower()] = node.id

    for tok in tokens:
        key = tok.lower().strip()
        if key in alias_index:
            nid = alias_index[key]
            node = store.get_node(nid)
            if node is None:
                unresolved.append(tok)
                continue
            # system filter: allow system match or "all" primitives
            node_sys = str(node.attrs.get("system") or "all")
            if system != "all" and node_sys not in (system, "all") and not nid.startswith(system):
                unresolved.append(tok)
                continue
            resolved.append(nid)
        else:
            # direct id lookup
            node = store.get_node(tok)
            if node is not None:
                resolved.append(node.id)
            else:
                unresolved.append(tok)
    # stable unique
    seen: set[str] = set()
    uniq: list[str] = []
    for r in resolved:
        if r not in seen:
            seen.add(r)
            uniq.append(r)
    return uniq, unresolved
