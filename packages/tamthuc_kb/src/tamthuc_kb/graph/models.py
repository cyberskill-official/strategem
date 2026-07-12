from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, field_validator

from tamthuc_kb.graph.taxonomy import EdgeRel, NodeKind


class Node(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str
    kind: NodeKind
    label: str = ""
    attrs: dict[str, Any] = {}

    @field_validator("kind", mode="before")
    @classmethod
    def _kind(cls, v: object) -> object:
        if isinstance(v, str) and v not in NodeKind.__members__.values() and v not in NodeKind:
            # also accept enum values
            try:
                return NodeKind(v)
            except ValueError as e:
                raise ValueError(f"unknown node kind: {v}") from e
        return v


class Edge(BaseModel):
    model_config = ConfigDict(extra="forbid")
    src: str
    rel: EdgeRel
    dst: str
    attrs: dict[str, Any] = {}

    @field_validator("rel", mode="before")
    @classmethod
    def _rel(cls, v: object) -> object:
        if isinstance(v, str):
            try:
                return EdgeRel(v)
            except ValueError as e:
                raise ValueError(f"unknown edge rel: {v}") from e
        return v
