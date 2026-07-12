from __future__ import annotations

from tamthuc_rag.ethics import EthicsSeverity, check_ethics, policy_action
from tamthuc_rag.schema import AIDisclosure, CitationCard, Interpretation


def _base(**kwargs: object) -> Interpretation:
    data = dict(
        beginner="Educational note.",
        expert="Technical note.",
        recommendations=[{"text": "Consider timing.", "citations": ["yba_1"]}],
        citations=[CitationCard(citation_id="yba_1", layers={"han": "青", "dich": "x"})],
        confidence=0.7,
        requires_human_review=False,
        ai_disclosure=AIDisclosure(
            model="stub",
            prompt_version="1",
            retrieved_citation_ids=["yba_1"],
        ),
    )
    data.update(kwargs)
    return Interpretation.model_validate(data)


def test_clean_ok() -> None:
    assert check_ethics(_base()) == []
    assert policy_action([]) == "allow"


def test_language_blocks() -> None:
    f = check_ethics(_base(beginner="You will definitely win."))
    assert any(x.family == "language" and x.severity == EthicsSeverity.high for x in f)
    assert policy_action(f) == "block"


def test_school_medium() -> None:
    f = check_ethics(_base(expert="This is the only correct school."))
    assert policy_action(f) == "human_review"
