"""TASK-RAG-006 interpretation eval loop."""

from __future__ import annotations

from tamthuc_rag.eval.cases import EvalCase, load_cases, load_cases_from_path
from tamthuc_rag.eval.judge import Judge, StubJudge
from tamthuc_rag.eval.metrics import CaseScore, citation_scores, faithfulness, relevance
from tamthuc_rag.eval.run import EvalReport, GateResult, Thresholds, evaluate, gate

__all__ = [
    "EvalCase",
    "load_cases",
    "load_cases_from_path",
    "CaseScore",
    "faithfulness",
    "relevance",
    "citation_scores",
    "Judge",
    "StubJudge",
    "EvalReport",
    "Thresholds",
    "GateResult",
    "evaluate",
    "gate",
]
