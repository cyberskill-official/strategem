from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from tamthuc_report.models import (
    AIDisclosure,
    ChartSummary,
    Citation,
    Interpretation,
    ReportPattern,
    StructuredReport,
)
from tamthuc_report.pdf_export import export_pdf, render_html


def _report() -> StructuredReport:
    return StructuredReport(
        report_id=uuid4(),
        query_id=uuid4(),
        chart_summary=ChartSummary(
            he="ky_mon",
            dau_vao={"datetime": "2004-01-01"},
            lich_phap_summary="甲子",
        ),
        detected_patterns=[ReportPattern(id="p1", name="青龍返首", polarity="cat", cung=1)],
        interpretation=Interpretation(
            beginner="beginner text",
            expert="expert text",
            recommendations=["go carefully"],
        ),
        citations=[
            Citation(
                source="YBA",
                locator="1.1",
                han="青龍返首",
                bach_thoai="Thanh long",
                dich="Azure dragon",
            )
        ],
        confidence=0.7,
        ai_disclosure=AIDisclosure(model="stub", limits="edu only", review_status="not_required"),
        created_at=datetime(2004, 1, 1, tzinfo=UTC),
    )


def test_export_has_pdf_header_and_sections() -> None:
    r = _report()
    pdf = export_pdf(r)
    assert pdf.startswith(b"%PDF")
    html = render_html(r)
    assert 'data-panel="engine"' in html
    assert 'data-panel="ai"' in html
    assert "AIDisclosure" in html
    assert "青龍返首" in html
    assert "stub" in html


def test_readonly() -> None:
    r = _report()
    before = r.model_dump()
    _ = export_pdf(r)
    assert r.model_dump() == before
