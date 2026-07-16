"""Auto-graded chart practice — TASK-EDU-002 (engine as grader)."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class GradeResult(BaseModel):
    model_config = ConfigDict(extra="forbid")
    passed: bool
    score: float
    expected_ids: list[str] = Field(default_factory=list)
    student_ids: list[str] = Field(default_factory=list)
    feedback: str


def grade_chart_practice(
    student_cach_cuc_ids: list[str],
    engine_envelope: dict[str, Any],
) -> GradeResult:
    """Compare student-detected ids against engine envelope cach_cuc (read-only)."""
    expected: list[str] = []
    raw = engine_envelope.get("cach_cuc") or []
    if isinstance(raw, list):
        for c in raw:
            if isinstance(c, dict) and c.get("id"):
                expected.append(str(c["id"]))
            elif isinstance(c, str):
                expected.append(c)
    exp_set = set(expected)
    stu_set = set(student_cach_cuc_ids)
    if not exp_set:
        return GradeResult(
            passed=True,
            score=1.0,
            expected_ids=[],
            student_ids=list(stu_set),
            feedback="no engine patterns to grade against",
        )
    inter = exp_set & stu_set
    score = len(inter) / len(exp_set)
    return GradeResult(
        passed=score >= 0.8,
        score=score,
        expected_ids=sorted(exp_set),
        student_ids=sorted(stu_set),
        feedback=f"matched {len(inter)}/{len(exp_set)} patterns",
    )
