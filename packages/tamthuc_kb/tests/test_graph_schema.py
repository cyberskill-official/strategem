from __future__ import annotations

import pytest
from pydantic import ValidationError
from tamthuc_kb.graph.models import Edge, Node
from tamthuc_kb.graph.seed import seed_ngu_hanh
from tamthuc_kb.graph.store import InMemoryGraphStore
from tamthuc_kb.graph.taxonomy import EdgeRel, NodeKind


def test_closed_node_kind() -> None:
    with pytest.raises(ValidationError):
        Node(id="x", kind="not_a_kind")  # type: ignore[arg-type]


def test_closed_edge_rel() -> None:
    with pytest.raises(ValidationError):
        Edge(src="a", rel="nope", dst="b")  # type: ignore[arg-type]


def test_seed_ngu_hanh() -> None:
    s = InMemoryGraphStore()
    seed_ngu_hanh(s)
    assert len(s.nodes_by_kind(NodeKind.ngu_hanh)) == 5
    sinh = s.neighbors("ngu_hanh_moc", EdgeRel.sinh)
    assert any(e.dst == "ngu_hanh_hoa" for e in sinh)
    khac = s.neighbors("ngu_hanh_moc", EdgeRel.khac)
    assert any(e.dst == "ngu_hanh_tho" for e in khac)


def test_edge_requires_endpoints() -> None:
    s = InMemoryGraphStore()
    with pytest.raises(ValueError):
        s.upsert_edge(Edge(src="a", rel=EdgeRel.sinh, dst="b"))
