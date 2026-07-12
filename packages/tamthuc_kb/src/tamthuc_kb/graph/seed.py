"""Minimal graph seed for ngu hanh + can/chi — FR-KB-001."""

from __future__ import annotations

from tamthuc_kb.graph.models import Edge, Node
from tamthuc_kb.graph.store import GraphStore
from tamthuc_kb.graph.taxonomy import EdgeRel, NodeKind


def seed_ngu_hanh(store: GraphStore) -> None:
    phases = ["moc", "hoa", "tho", "kim", "thuy"]
    for p in phases:
        store.upsert_node(Node(id=f"ngu_hanh_{p}", kind=NodeKind.ngu_hanh, label=p))
    # sinh cycle
    sinh = list(zip(phases, phases[1:] + phases[:1], strict=True))
    for a, b in sinh:
        store.upsert_edge(Edge(src=f"ngu_hanh_{a}", rel=EdgeRel.sinh, dst=f"ngu_hanh_{b}"))
    # khac cycle: moc->tho->thuy->hoa->kim->moc
    khac_order = ["moc", "tho", "thuy", "hoa", "kim"]
    for a, b in zip(khac_order, khac_order[1:] + khac_order[:1], strict=True):
        store.upsert_edge(Edge(src=f"ngu_hanh_{a}", rel=EdgeRel.khac, dst=f"ngu_hanh_{b}"))
