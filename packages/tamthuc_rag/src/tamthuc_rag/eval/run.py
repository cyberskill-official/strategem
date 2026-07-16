"""Eval run + CI gate — TASK-RAG-006."""

from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from tamthuc_rag.eval.cases import EvalCase
from tamthuc_rag.eval.judge import Judge
from tamthuc_rag.eval.metrics import CaseScore, score_case
from tamthuc_rag.prompt_builder import PROMPT_VERSION
from tamthuc_rag.schema import Interpretation


class Thresholds(BaseModel):
    model_config = ConfigDict(extra="forbid")
    faithfulness: float = 0.90
    relevance: float = 0.80
    citation_f1: float = 0.85
    max_regression_delta: float = 0.03


class EvalReport(BaseModel):
    model_config = ConfigDict(extra="forbid")
    prompt_version: str
    judge_version: str | None = None
    n_cases: int
    faithfulness: float
    relevance: float
    citation_precision: float
    citation_recall: float
    citation_f1: float
    per_case: list[CaseScore] = Field(default_factory=list)
    regressions: list[str] = Field(default_factory=list)
    baseline_ref: str | None = None
    advisory_judge_band: float | None = None


class GateResult(BaseModel):
    model_config = ConfigDict(extra="forbid")
    passed: bool
    failing_metrics: list[str] = Field(default_factory=list)
    regressed_cases: list[str] = Field(default_factory=list)
    message: str = ""


InterpretFn = Callable[[EvalCase], tuple[Interpretation, set[str]]]


def _mean(vals: list[float]) -> float:
    return sum(vals) / len(vals) if vals else 0.0


def _f1(p: float, r: float) -> float:
    if p + r == 0:
        return 0.0
    return 2 * p * r / (p + r)


def evaluate(
    cases: list[EvalCase],
    interpret_fn: InterpretFn,
    thresholds: Thresholds | None = None,
    baseline: EvalReport | dict[str, Any] | None = None,
    judge: Judge | None = None,
    *,
    prompt_version: str | None = None,
) -> EvalReport:
    thr = thresholds or Thresholds()
    per_case: list[CaseScore] = []
    judge_scores: list[float] = []
    for case in cases:
        interp, retrieved = interpret_fn(case)
        cs = score_case(
            case,
            interp,
            retrieved,
            pass_thresholds={
                "faithfulness": thr.faithfulness,
                "relevance": thr.relevance,
                "citation_f1": thr.citation_f1,
            },
        )
        per_case.append(cs)
        if judge is not None:
            claim = f"{interp.beginner} {interp.expert}"
            passage = case.meaning_classical
            judge_scores.append(judge.entails(claim, passage))

    faithfulness_m = _mean([c.faithfulness for c in per_case])
    relevance_m = _mean([c.relevance for c in per_case])
    prec_m = _mean([c.citation_precision for c in per_case])
    rec_m = _mean([c.citation_recall for c in per_case])
    f1_m = _f1(prec_m, rec_m)

    baseline_report: EvalReport | None = None
    if baseline is not None:
        baseline_report = (
            baseline if isinstance(baseline, EvalReport) else EvalReport.model_validate(baseline)
        )

    regressions: list[str] = []
    if baseline_report is not None:
        base_by_id = {c.case_id: c for c in baseline_report.per_case}
        for cs in per_case:
            prev = base_by_id.get(cs.case_id)
            if prev is None:
                continue
            for attr in ("faithfulness", "relevance", "citation_precision", "citation_recall"):
                if getattr(prev, attr) - getattr(cs, attr) > thr.max_regression_delta:
                    regressions.append(cs.case_id)
                    break

    return EvalReport(
        prompt_version=prompt_version or PROMPT_VERSION,
        judge_version=getattr(judge, "version", None) if judge else None,
        n_cases=len(cases),
        faithfulness=faithfulness_m,
        relevance=relevance_m,
        citation_precision=prec_m,
        citation_recall=rec_m,
        citation_f1=f1_m,
        per_case=per_case,
        regressions=sorted(set(regressions)),
        baseline_ref=baseline_report.prompt_version if baseline_report else None,
        advisory_judge_band=_mean(judge_scores) if judge_scores else None,
    )


def gate(
    report: EvalReport,
    thresholds: Thresholds,
    baseline: EvalReport | dict[str, Any] | None = None,
) -> GateResult:
    failing: list[str] = []
    if report.faithfulness < thresholds.faithfulness:
        failing.append("faithfulness")
    if report.relevance < thresholds.relevance:
        failing.append("relevance")
    if report.citation_f1 < thresholds.citation_f1:
        failing.append("citation_f1")

    regressed = list(report.regressions)
    if baseline is not None:
        base = baseline if isinstance(baseline, EvalReport) else EvalReport.model_validate(baseline)
        for metric in ("faithfulness", "relevance", "citation_f1"):
            regressed_metric = (
                getattr(base, metric) - getattr(report, metric) > thresholds.max_regression_delta
            )
            if regressed_metric and f"regression:{metric}" not in failing and metric not in failing:
                failing.append(f"regression:{metric}")
        regressed = sorted(set(regressed + report.regressions))

    passed = not failing and not regressed
    msg_parts: list[str] = []
    if failing:
        msg_parts.append(f"failing metrics: {', '.join(failing)}")
    if regressed:
        msg_parts.append(f"regressed cases: {', '.join(regressed)}")
    return GateResult(
        passed=passed,
        failing_metrics=failing,
        regressed_cases=regressed,
        message="; ".join(msg_parts) if msg_parts else "ok",
    )


def load_baseline(path: Path | str | None = None) -> EvalReport:
    p = Path(path) if path else Path(__file__).with_name("baseline.json")
    return EvalReport.model_validate(json.loads(p.read_text(encoding="utf-8")))


def stub_interpret(case: EvalCase) -> tuple[Interpretation, set[str]]:
    """Deterministic stub interpreter for CI — cites expected + conveys polarity."""
    from tamthuc_rag.schema import AIDisclosure, CitationCard

    retrieved = set(case.expected_citations) or {f"{case.id}_src"}
    polarity_word = {
        "cat": "auspicious (cát)",
        "hung": "inauspicious (hung) — use caution",
        "trung": "neutral / mixed",
    }.get(case.expected_polarity, case.expected_polarity)
    beginner = (
        f"For '{case.id}', the classical reading is {polarity_word}. "
        f"Decision support only. Pattern cue: {case.meaning_classical[:80]}"
    )
    expert = f"Technical note for {case.id}: polarity={case.expected_polarity}."
    cards = [
        CitationCard(citation_id=cid, layers={"han": case.meaning_classical[:40]}, locator="eval")
        for cid in sorted(retrieved)
    ]
    disc = AIDisclosure(
        model="stub-eval",
        prompt_version=PROMPT_VERSION,
        retrieved_citation_ids=sorted(retrieved),
    )
    interp = Interpretation(
        beginner=beginner,
        expert=expert,
        recommendations=[{"text": "Weigh the cited classical guidance against your context."}],
        citations=cards,
        confidence=0.85,
        requires_human_review=False,
        ai_disclosure=disc,
    )
    return interp, retrieved
