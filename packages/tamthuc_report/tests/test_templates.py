"""TASK-REPORT-003 template tests."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from tamthuc_report.models import (
    AIDisclosure,
    ChartSummary,
    Interpretation,
    StructuredReport,
)
from tamthuc_report.templates import render_sections, template_for


def _report() -> StructuredReport:
    return StructuredReport(
        report_id=uuid4(),
        query_id=uuid4(),
        chart_summary=ChartSummary(
            he="ky_mon",
            dau_vao={"loai_cau_hoi": "trach_thoi"},
            lich_phap_summary="sample",
            key_positions=["a"],
        ),
        detected_patterns=[],
        interpretation=Interpretation(beginner="b", expert="e", recommendations=["r1"]),
        citations=[],
        confidence=0.5,
        ai_disclosure=AIDisclosure(
            model="stub", limits="decision support", review_status="not_required"
        ),
        created_at=datetime.now(UTC),
    )


def test_template_for_mapping() -> None:
    t = template_for("trach_thoi")
    assert t.he == ["ky_mon", "luc_nham"]
    assert "ky_mon" in template_for("phuong_vi").he
    assert "thai_at" in template_for("chu_khach").he
    assert template_for("vi_mo").he == ["thai_at"]
    # unknown -> default
    d = template_for("unknown_xyz")
    assert d.question_type == "default"


def test_render_readonly() -> None:
    report = _report()
    before = report.model_dump()
    tmpl = template_for("chu_khach")
    sections = render_sections(report, tmpl)
    assert [s.id for s in sections][0] == "interpretation"
    assert report.model_dump() == before
    # content set-equality
    ids = {s.id for s in sections}
    assert "chart_summary" in ids
    assert "confidence" in ids
