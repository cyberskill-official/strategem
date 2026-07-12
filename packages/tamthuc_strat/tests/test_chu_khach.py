"""FR-STRAT-003 chu-khach framework tests."""

from __future__ import annotations

import copy
import json

from tamthuc_strat.chu_khach import DecisionFrame, build_frame


def _golden_interp() -> dict[str, object]:
    return {
        "beginner": "the acting side holds the initiative this window",
        "expert": "dung than on the acting palace supports measured advance",
        "recommendations": [
            {"text": "a cat cach cuc sits on the acting palace", "citations": ["yba_dieu_012"]}
        ],
        "citations": [{"citation_id": "yba_dieu_012"}],
        "ai_disclosure": {
            "model": "gpt-4o-mini",
            "limits": "decision support, not a verdict; no medical/legal/financial advice",
            "review_status": "not_required",
            "retrieved_citation_ids": ["yba_dieu_012"],
        },
    }


def _golden_laso() -> dict[str, object]:
    return {
        "question": "Should we enter the northern market this quarter?",
        "charts": {
            "qimen": {
                "ban": {
                    "dung_than": {
                        "chu": "nhat can",
                        "khach": "ung than",
                        "chu_cung": 1,
                        "khach_cung": 7,
                    }
                }
            }
        },
    }


def test_build_frame_four_steps_per_lens() -> None:
    laso = _golden_laso()
    interp = _golden_interp()
    for lens, chu, khach in (
        ("competitor", "us", "the competitor"),
        ("risk", "the action we take", "the external event"),
        ("partner", "us", "the partner / hire"),
    ):
        frame = build_frame(laso, interp, lens)  # type: ignore[arg-type]
        assert isinstance(frame, DecisionFrame)
        assert len(frame.step1_framing) == 2
        assert frame.step1_framing[0].role_label == chu
        assert frame.step1_framing[1].role_label == khach
        assert frame.step2_signals
        assert frame.step3_context_prompts
        assert "decide" in frame.step4_decision.prompt.lower()
        assert frame.step4_decision.disclosure.model


def test_signals_citations_subset() -> None:
    frame = build_frame(_golden_laso(), _golden_interp(), "competitor")
    allowed = {"yba_dieu_012"}
    for s in frame.step2_signals:
        assert s.citations
        assert set(s.citations).issubset(allowed)


def test_read_only_inputs() -> None:
    laso = _golden_laso()
    interp = _golden_interp()
    before_l = json.dumps(laso, sort_keys=True)
    before_i = json.dumps(interp, sort_keys=True)
    la_copy = copy.deepcopy(laso)
    in_copy = copy.deepcopy(interp)
    _ = build_frame(la_copy, in_copy, "risk")
    assert json.dumps(la_copy, sort_keys=True) == before_l
    assert json.dumps(in_copy, sort_keys=True) == before_i
    assert json.dumps(laso, sort_keys=True) == before_l
    assert json.dumps(interp, sort_keys=True) == before_i


def test_handoff_not_verdict() -> None:
    frame = build_frame(_golden_laso(), _golden_interp(), "partner")
    text = frame.step4_decision.prompt.lower()
    assert "you will" not in text
    assert "guaranteed" not in text
    assert "decide" in text
