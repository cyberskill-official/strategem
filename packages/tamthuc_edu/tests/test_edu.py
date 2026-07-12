"""FR-EDU-001..004 smoke tests."""

from __future__ import annotations

from tamthuc_edu.curriculum import curriculum_levels, progression_ok
from tamthuc_edu.grade import grade_chart_practice
from tamthuc_edu.library import ClassicalLibrary, LibraryEntry
from tamthuc_edu.onboarding import help_topics, onboarding_path


def test_four_levels() -> None:
    levels = curriculum_levels()
    assert len(levels) == 4
    assert levels[0].id == "L1"
    assert levels[-1].id == "L4"
    completed = set(levels[0].criteria) | set(levels[1].criteria)
    assert progression_ok(completed, "L3") is True
    assert progression_ok(set(), "L3") is False


def test_grade_against_engine() -> None:
    env = {"cach_cuc": [{"id": "a"}, {"id": "b"}]}
    g = grade_chart_practice(["a", "b"], env)
    assert g.passed and g.score == 1.0
    g2 = grade_chart_practice(["a"], env)
    assert g2.score == 0.5
    assert not g2.passed


def test_library_search() -> None:
    lib = ClassicalLibrary(
        [
            LibraryEntry(
                unit_id="u1",
                title="Thanh long",
                han="青龍",
                bach_thoai="Thanh long",
                dich="Azure dragon",
            )
        ]
    )
    assert lib.search("青龍")
    assert lib.search("azure", lang="en")


def test_onboarding() -> None:
    path = onboarding_path()
    assert len(path) >= 3
    assert "verdict" in path[-1].body.lower() or "decide" in path[-1].title.lower()
    assert help_topics()
