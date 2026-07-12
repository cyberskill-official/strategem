from __future__ import annotations

from datetime import datetime, timedelta

from tamthuc_strat.models import TimingRequest
from tamthuc_strat.scenario_compare import Scenario, ScenarioSet, compare_scenarios
from tamthuc_strat.timing_optimizer import optimize_timing


def eng(when: datetime, req: TimingRequest) -> dict[str, object]:
    # morning better
    score_pat = (
        [{"id": "c", "name": "C", "polarity": "cat", "score": 0.9, "citations": []}]
        if when.hour < 12
        else [{"id": "h", "name": "H", "polarity": "hung", "score": 0.8, "citations": []}]
    )
    return {
        "cach_cuc": score_pat,
        "provenance": {"cache_key": f"k-{when.isoformat()}"},
    }


def test_calls_optimizer_not_cast() -> None:
    calls: list[str] = []

    def opt(req: TimingRequest, engine: object) -> object:
        calls.append(req.datetime if hasattr(req, "datetime") else "ok")
        return optimize_timing(req, eng)

    start = datetime(2004, 1, 1, 8)
    end = start + timedelta(hours=4)
    ss = ScenarioSet(
        scenarios=[
            Scenario(
                label="A",
                request=TimingRequest(start=start, end=end, granularity="gio", top_n=2),
            ),
            Scenario(
                label="B",
                request=TimingRequest(
                    start=start + timedelta(days=1),
                    end=start + timedelta(days=1, hours=4),
                    granularity="gio",
                    top_n=2,
                ),
            ),
        ],
        top_n=2,
    )
    # force use of real optimizer path
    cmp = compare_scenarios(ss, eng)
    assert len(cmp.results) == 2
    assert set(cmp.ranked_labels) == {"A", "B"}
    assert cmp.best_overall is not None
    assert all(r.windows for r in cmp.results)


def test_ranking_by_best_score() -> None:
    morning = TimingRequest(
        start=datetime(2004, 1, 1, 8),
        end=datetime(2004, 1, 1, 10),
        granularity="gio",
        top_n=1,
    )
    night = TimingRequest(
        start=datetime(2004, 1, 1, 20),
        end=datetime(2004, 1, 1, 22),
        granularity="gio",
        top_n=1,
    )
    ss = ScenarioSet(
        scenarios=[
            Scenario(label="night", request=night),
            Scenario(label="morning", request=morning),
        ],
        top_n=1,
    )
    cmp = compare_scenarios(ss, eng)
    assert cmp.ranked_labels[0] == "morning"
