"""Four-level curriculum — FR-EDU-001."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class Level(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str
    name: str
    order: int
    criteria: list[str] = Field(default_factory=list)
    unlocks: list[str] = Field(default_factory=list)


def curriculum_levels() -> list[Level]:
    return [
        Level(
            id="L1",
            name="Foundations",
            order=1,
            criteria=["identify_ban_components", "read_polarity_badge"],
            unlocks=["cast_demo"],
        ),
        Level(
            id="L2",
            name="Single-system cast",
            order=2,
            criteria=["cast_qimen", "match_one_cach_cuc"],
            unlocks=["practice_grader"],
        ),
        Level(
            id="L3",
            name="Interpretation with citations",
            order=3,
            criteria=["cite_classical", "no_verdict_framing"],
            unlocks=["report_view"],
        ),
        Level(
            id="L4",
            name="Cross-system comparison",
            order=4,
            criteria=["compare_two_systems", "scope_awareness"],
            unlocks=["cross_system_validate"],
        ),
    ]


def progression_ok(completed: set[str], target_level: str) -> bool:
    levels = curriculum_levels()
    by_id = {lv.id: lv for lv in levels}
    target = by_id.get(target_level)
    if target is None:
        return False
    # all prior levels' criteria must be completed
    for lv in levels:
        if lv.order >= target.order:
            break
        if not set(lv.criteria).issubset(completed):
            return False
    return True
