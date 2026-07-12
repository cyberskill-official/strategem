"""Scenario Comparison — FR-STRAT-002. Thin composition over STRAT-001."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from tamthuc_strat.models import ScoredWindow, TimingRequest, TimingResult
from tamthuc_strat.timing_optimizer import EngineFn, optimize_timing

OptimizerFn = Callable[[TimingRequest, EngineFn], TimingResult]


class Scenario(BaseModel):
    model_config = ConfigDict(extra="forbid")
    label: str
    request: TimingRequest


class ScenarioSet(BaseModel):
    model_config = ConfigDict(extra="forbid")
    scenarios: list[Scenario]
    top_n: int = 3


class ScenarioResult(BaseModel):
    model_config = ConfigDict(extra="forbid")
    label: str
    windows: list[ScoredWindow] = Field(default_factory=list)
    best_score: float


class ScenarioComparison(BaseModel):
    model_config = ConfigDict(extra="forbid")
    results: list[ScenarioResult]
    ranked_labels: list[str]
    best_overall: ScoredWindow | None


def compare_scenarios(
    scenario_set: ScenarioSet,
    engine: EngineFn,
    *,
    optimizer: OptimizerFn = optimize_timing,
) -> ScenarioComparison:
    results: list[ScenarioResult] = []
    for sc in scenario_set.scenarios:
        req = sc.request.model_copy(update={"top_n": scenario_set.top_n})
        # STRAT-002 never casts/scores — only calls STRAT-001
        tr = optimizer(req, engine)
        windows = list(tr.windows)
        best = windows[0].score if windows else float("-inf")
        results.append(ScenarioResult(label=sc.label, windows=windows, best_score=best))

    def sort_key(r: ScenarioResult) -> tuple[float, Any, int]:
        earliest = r.windows[0].start if r.windows else None
        idx = next(i for i, s in enumerate(scenario_set.scenarios) if s.label == r.label)
        # higher score first; earlier best window; input order
        return (-r.best_score, earliest or 0, idx)

    ranked = sorted(results, key=sort_key)
    ranked_labels = [r.label for r in ranked]
    best_overall: ScoredWindow | None = None
    for r in ranked:
        if r.windows:
            best_overall = r.windows[0]
            break
    return ScenarioComparison(
        results=results,
        ranked_labels=ranked_labels,
        best_overall=best_overall,
    )
