"""TASK-RAG-006 interpretation eval loop tests."""

from __future__ import annotations

import json
from pathlib import Path

from tamthuc_rag.eval.cases import EvalCase, load_cases, load_cases_from_path
from tamthuc_rag.eval.judge import StubJudge
from tamthuc_rag.eval.metrics import citation_scores, faithfulness, relevance
from tamthuc_rag.eval.run import (
    Thresholds,
    evaluate,
    gate,
    load_baseline,
    stub_interpret,
)
from tamthuc_rag.prompt_builder import PROMPT_VERSION
from tamthuc_rag.schema import AIDisclosure, CitationCard, Interpretation

FIX = Path(__file__).parent / "fixtures" / "eval_cases_sample.json"
BASELINE = Path(__file__).resolve().parents[1] / "src" / "tamthuc_rag" / "eval" / "baseline.json"
SCHEMA = Path(__file__).resolve().parents[3] / "docs" / "contracts" / "eval-report.schema.json"


def _interp(
    beginner: str,
    expert: str = "",
    cites: list[str] | None = None,
    recs: list[dict[str, object]] | None = None,
) -> Interpretation:
    cards = [CitationCard(citation_id=c) for c in (cites or [])]
    recommendations: list[dict[str, object]] = (
        list(recs) if recs is not None else [{"text": "weigh context"}]
    )
    return Interpretation(
        beginner=beginner,
        expert=expert,
        recommendations=recommendations,
        citations=cards,
        confidence=0.8,
        requires_human_review=False,
        ai_disclosure=AIDisclosure(
            model="t",
            prompt_version=PROMPT_VERSION,
            retrieved_citation_ids=list(cites or []),
        ),
    )


def test_load_cases_from_kb_seed_band() -> None:
    cases = load_cases()
    assert 150 <= len(cases) <= 200
    assert all(c.expected_citations for c in cases if c.system == "qimen")
    assert all(c.version >= 1 for c in cases)


def test_load_fixture_cases() -> None:
    cases = load_cases_from_path(FIX)
    assert len(cases) == 4
    assert cases[0].id == "qimen_thanh_long_hoi_dau"


def test_faithfulness_lower_bound() -> None:
    retrieved = {"a", "b"}
    good = _interp("ok", cites=["a", "b"])
    assert faithfulness(good, retrieved) == 1.0
    bad_uncited = _interp("A long free-memory claim with no classical citation at all.")
    assert faithfulness(bad_uncited, retrieved) == 0.0
    fabricated = _interp("claim", cites=["fabricated"])
    assert faithfulness(fabricated, retrieved) == 0.0


def test_citation_precision_recall() -> None:
    interp = _interp("x", cites=["a", "x"])
    p, r = citation_scores(interp, ["a", "b"])
    assert p == 0.5
    assert r == 0.5


def test_relevance_polarity() -> None:
    case = EvalCase(
        id="pat_cat",
        version=1,
        system="qimen",
        query="business timing decision window",
        conditions={},
        expected_polarity="cat",
        meaning_classical="青龍",
        expected_citations=["c1"],
    )
    good = _interp("auspicious (cát) reading of pat_cat for the decision", cites=["c1"])
    assert relevance(good, case) >= 0.5
    bad = _interp("random text", cites=["c1"], recs=[])
    # still may get partial if recommendations empty and no polarity
    assert relevance(bad, case) < relevance(good, case)


def test_score_case_and_gate_absolute() -> None:
    cases = load_cases_from_path(FIX)
    report = evaluate(cases[:3], stub_interpret, Thresholds())
    assert report.n_cases == 3
    assert report.prompt_version == PROMPT_VERSION
    result = gate(report, Thresholds(faithfulness=0.90, relevance=0.5, citation_f1=0.5))
    assert result.passed is True


def test_gate_fails_below_threshold() -> None:
    case = EvalCase(
        id="trap",
        version=1,
        system="qimen",
        query="q",
        conditions={},
        expected_polarity="cat",
        meaning_classical="m",
        expected_citations=["must"],
    )

    def bad_fn(c: EvalCase) -> tuple[Interpretation, set[str]]:
        return _interp("uncited free memory claim that is long enough to fail", recs=[]), {"must"}

    report = evaluate([case], bad_fn, Thresholds())
    result = gate(report, Thresholds(faithfulness=0.90, relevance=0.99, citation_f1=0.99))
    assert result.passed is False
    assert result.failing_metrics


def test_gate_fails_on_regression() -> None:
    cases = load_cases_from_path(FIX)[:2]
    good = evaluate(cases, stub_interpret, Thresholds())

    # degrade second run citations
    def worse(c: EvalCase) -> tuple[Interpretation, set[str]]:
        interp, retrieved = stub_interpret(c)
        # drop all citations
        empty = _interp(
            interp.beginner,
            interp.expert,
            cites=[],
            recs=list(interp.recommendations),
        )
        return empty, retrieved

    bad = evaluate(cases, worse, Thresholds(), baseline=good)
    result = gate(bad, Thresholds(max_regression_delta=0.03), baseline=good)
    assert result.passed is False
    assert result.regressed_cases or any("regression" in m for m in result.failing_metrics)


def test_determinism_stub_eval() -> None:
    cases = load_cases_from_path(FIX)
    r1 = evaluate(cases[:3], stub_interpret, Thresholds())
    r2 = evaluate(cases[:3], stub_interpret, Thresholds())
    assert r1.model_dump() == r2.model_dump()


def test_baseline_committed_and_valid() -> None:
    baseline = load_baseline(BASELINE)
    assert baseline.prompt_version
    assert baseline.n_cases >= 1
    # re-run stub on sample should meet or beat baseline under soft thresholds
    cases = load_cases_from_path(FIX)[: baseline.n_cases]
    report = evaluate(cases[:3], stub_interpret, Thresholds(), baseline=baseline)
    thr = Thresholds(faithfulness=0.5, relevance=0.3, citation_f1=0.5, max_regression_delta=0.5)
    assert gate(report, thr, baseline=baseline).passed is True


def test_judge_advisory_not_hard_gate() -> None:
    cases = load_cases_from_path(FIX)[:2]
    report = evaluate(cases, stub_interpret, Thresholds(), judge=StubJudge(0.95))
    assert report.judge_version == "stub-judge@1"
    assert report.advisory_judge_band is not None
    # even with judge, gate only uses deterministic metrics
    thr = Thresholds(faithfulness=0.5, relevance=0.3, citation_f1=0.5)
    assert gate(report, thr).passed is True


def test_eval_report_schema_shape() -> None:
    if not SCHEMA.exists():
        return
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    assert schema.get("title") == "EvalReport" or "properties" in schema
    required = set(schema.get("required") or [])
    report = evaluate(load_cases_from_path(FIX)[:1], stub_interpret)
    for key in required:
        assert key in report.model_dump()
