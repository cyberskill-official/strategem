"""Curation review queue — TASK-KB-004."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from tamthuc_kb.curation.models import ReviewItem, ReviewObjectType, ReviewState


class CurationQueue:
    def __init__(self) -> None:
        self._items: dict[str, ReviewItem] = {}
        self._history: list[ReviewItem] = []

    def submit(
        self,
        object_type: ReviewObjectType,
        object_id: str,
        version: int,
        payload: dict[str, Any],
        by: str,
    ) -> ReviewItem:
        item = ReviewItem(
            id=str(uuid4()),
            object_type=object_type,
            object_id=object_id,
            object_version=version,
            state=ReviewState.in_review,
            submitted_by=by,
            submitted_at=datetime.now(UTC),
            payload=dict(payload),
        )
        self._items[item.id] = item
        return item

    def pending(self) -> list[ReviewItem]:
        return [i for i in self._items.values() if i.state == ReviewState.in_review]

    def get(self, item_id: str) -> ReviewItem | None:
        return self._items.get(item_id)

    def update(self, item: ReviewItem) -> ReviewItem:
        self._items[item.id] = item
        self._history.append(item.model_copy(deep=True))
        return item

    def accepted_versions(self) -> dict[tuple[str, str], int]:
        """Map (object_type, object_id) -> highest accepted version."""
        out: dict[tuple[str, str], int] = {}
        for i in self._items.values():
            if i.state == ReviewState.accepted:
                key = (i.object_type.value, i.object_id)
                out[key] = max(out.get(key, 0), i.object_version)
        return out
