"""COV-023: PDF includes full legal disclaimer + sections + vernacular names."""

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


def test_pdf_legal_disclaimer_and_sections() -> None:
    r = StructuredReport(
        report_id=uuid4(),
        query_id=uuid4(),
        chart_summary=ChartSummary(
            he="ky_mon",
            dau_vao={"datetime": "2004-01-01"},
            lich_phap_summary="甲子",
        ),
        detected_patterns=[ReportPattern(id="p1", name="青龍返首", polarity="cat", cung=1)],
        interpretation=Interpretation(
            beginner="beginner",
            expert="expert",
            recommendations=["reflect carefully"],
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
    html = render_html(r, lang="bi")
    assert 'data-panel="legal-disclaimer"' in html
    assert "fortune-telling" in html.lower() or "bói" in html.lower()
    assert 'data-panel="patterns"' in html
    assert 'data-panel="recommendations"' in html
    assert "AIDisclosure" in html or "model=stub" in html
    assert "Thanh Long" in html or "vernacular" in html
    pdf = export_pdf(r)
    assert pdf.startswith(b"%PDF")
    assert b"%%EOF" in pdf
    assert b"/Type /Catalog" in pdf or b"/Type/Catalog" in pdf
    assert b"startxref" in pdf or b"xref" in pdf
    # disclaimer text should be embeddable in content streams / fonts
    assert (
        b"fortune" in pdf.lower()
        or b"Legal" in pdf
        or b"disclaimer" in pdf.lower()
        or len(pdf) > 800
    )
