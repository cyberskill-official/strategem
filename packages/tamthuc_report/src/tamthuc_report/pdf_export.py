"""PDF export — TASK-REPORT-002. ReportLab renderer (real PDF structure)."""

from __future__ import annotations

from io import BytesIO
from typing import Any, Literal

from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

from tamthuc_report.models import StructuredReport

# COV-023: full legal disclaimer (VOICE / LEGAL) — always on PDF
FULL_LEGAL_DISCLAIMER_VI = (
    "Tuyên bố pháp lý: Tài liệu này chỉ dùng để suy nghĩ và học hỏi văn hoá "
    "Tam Thức. Không phải lời bói chắc chắn, không thay thế tư vấn y tế, "
    "pháp lý hay tài chính. Quyết định cuối cùng thuộc về người đọc."
)
FULL_LEGAL_DISCLAIMER_EN = (
    "Legal disclaimer: This document is for cultural reflection and learning only. "
    "It is not fortune-telling and not a substitute for medical, legal, or financial advice. "
    "Final decisions remain with the reader."
)

_UMBER = HexColor("#45210E")
_OCHRE = HexColor("#F4BA17")


def _vernacular_pattern_name(name: str) -> str:
    """Prefer human-facing names; keep classical as secondary when mixed."""
    table = {
        "青龍返首": "Thanh Long Phản Thủ",
        "飛鳥跌穴": "Phi Điểu Điệt Huyệt",
        "白虎猖狂": "Bạch Hổ Xương Cuồng",
        "門迫": "Môn Bách",
        "元首": "Nguyên Thủ",
        "掩": "Yểm",
    }
    return table.get(name, name)


def _coerce_report(report: StructuredReport | dict[str, Any]) -> StructuredReport:
    if isinstance(report, StructuredReport):
        return report
    return StructuredReport.model_validate(report)


def render_html(
    report: StructuredReport | dict[str, Any], lang: Literal["vi", "en", "bi"] = "bi"
) -> str:
    """Read-only HTML layout of StructuredReport (preview / print CSS)."""
    report = _coerce_report(report)
    patterns_rows = "".join(
        (
            f"<tr><td><span class='vernacular'>{_vernacular_pattern_name(p.name)}</span>"
            f"{f' <span class="classical">{p.name}</span>' if _vernacular_pattern_name(p.name) != p.name else ''}"
            f"</td><td>{p.polarity}</td><td>{p.cung or ''}</td></tr>"
        )
        for p in report.detected_patterns
    )
    cites = "".join(
        f"<li><strong>{c.source}</strong> [{c.locator}] "
        f"漢:{c.han or '—'} · BT:{c.bach_thoai or '—'} · D:{c.dich or '—'}</li>"
        for c in report.citations
    )
    beginner = report.interpretation.beginner
    expert = report.interpretation.expert
    disc = report.ai_disclosure
    recs = report.interpretation.recommendations
    rec_items = "".join(
        f"<li>{r if isinstance(r, str) else (r.get('text') if isinstance(r, dict) else r)}</li>"
        for r in recs
    )
    disclaimer = (
        f"<p>{FULL_LEGAL_DISCLAIMER_VI}</p><p>{FULL_LEGAL_DISCLAIMER_EN}</p>"
        if lang == "bi"
        else f"<p>{FULL_LEGAL_DISCLAIMER_EN if lang == 'en' else FULL_LEGAL_DISCLAIMER_VI}</p>"
    )
    return f"""<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="utf-8"/>
<title>Report {report.report_id}</title>
<style>
  body {{ font-family: "Be Vietnam Pro", system-ui, sans-serif; color: #45210E; line-height: 1.55; }}
  .brand {{ background: #45210E; color: #F4BA17; padding: 12px 16px; }}
  .panel {{ border: 2px solid #F4BA17; padding: 12px; margin: 12px 0; background: #fff; }}
  .label {{ font-weight: 700; color: #45210E; }}
  .disclaimer {{ background: #FBF6EE; border-left: 4px solid #45210E; padding: 12px 16px; margin: 12px 0; }}
  .classical {{ color: #6b4a2e; font-size: 0.9em; }}
  .vernacular {{ font-weight: 600; }}
  @media print {{
    .panel {{ background: #fff !important; box-shadow: none; }}
    body {{ line-height: 1.55; }}
  }}
</style>
</head>
<body>
  <header class="brand">CyberSkill · Tam Thức Report</header>
  <p>report_id={report.report_id} · query_id={report.query_id} · {report.created_at.isoformat()}</p>

  <section class="disclaimer" data-panel="legal-disclaimer">
    <div class="label">Legal disclaimer</div>
    {disclaimer}
  </section>

  <section class="panel" data-panel="engine">
    <div class="label">Chart summary — deterministic</div>
    <p>he={report.chart_summary.he}</p>
    <p>{report.chart_summary.lich_phap_summary}</p>
  </section>

  <section class="panel" data-panel="patterns">
    <div class="label">Patterns (vernacular first)</div>
    <table><thead><tr><th>Pattern</th><th>Polarity</th><th>Cung</th></tr></thead>
    <tbody>{patterns_rows}</tbody></table>
  </section>

  <section class="panel" data-panel="ai">
    <div class="label">AI interpretation</div>
    <p data-lang="beginner">{beginner}</p>
    <p data-lang="expert">{expert}</p>
  </section>

  <section class="panel" data-panel="recommendations">
    <div class="label">Recommendations</div>
    <ul>{rec_items}</ul>
  </section>

  <section class="panel" data-panel="disclosure">
    <div class="label">AIDisclosure</div>
    <p>model={disc.model}</p>
    <p>limits={disc.limits}</p>
    <p>review_status={disc.review_status}</p>
    <p>is_ai_generated=true</p>
  </section>

  <section class="panel" data-panel="citations">
    <div class="label">Citations</div>
    <ol>{cites}</ol>
  </section>
  <!-- lang={lang} -->
</body>
</html>
"""


def _esc(text: str) -> str:
    return (
        text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")
    )


def export_pdf(
    report: StructuredReport | dict[str, Any],
    lang: Literal["vi", "en", "bi"] = "bi",
) -> bytes:
    """Produce a real PDF (ReportLab) with report sections + legal disclaimer."""
    report = _coerce_report(report)
    buf = BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=16 * mm,
        bottomMargin=16 * mm,
        title=f"Tam Thuc Report {report.report_id}",
        author="CyberSkill",
    )
    styles = getSampleStyleSheet()
    brand = ParagraphStyle(
        "Brand",
        parent=styles["Heading1"],
        textColor=_OCHRE,
        backColor=_UMBER,
        fontSize=14,
        spaceAfter=10,
        leading=18,
    )
    h2 = ParagraphStyle(
        "Section",
        parent=styles["Heading2"],
        textColor=_UMBER,
        fontSize=11,
        spaceBefore=10,
        spaceAfter=4,
    )
    body = ParagraphStyle(
        "Body",
        parent=styles["BodyText"],
        textColor=_UMBER,
        fontSize=9,
        leading=12,
        spaceAfter=4,
    )
    disclaimer_style = ParagraphStyle(
        "Disclaimer",
        parent=body,
        backColor=HexColor("#FBF6EE"),
        borderPadding=6,
        spaceAfter=8,
    )

    story: list[Any] = [
        Paragraph("CyberSkill · Tam Thức Report", brand),
        Paragraph(
            _esc(
                f"report_id={report.report_id} · query_id={report.query_id} · "
                f"{report.created_at.isoformat()}"
            ),
            body,
        ),
        Paragraph("Legal disclaimer", h2),
    ]
    if lang == "bi":
        story.append(Paragraph(_esc(FULL_LEGAL_DISCLAIMER_VI), disclaimer_style))
        story.append(Paragraph(_esc(FULL_LEGAL_DISCLAIMER_EN), disclaimer_style))
    elif lang == "en":
        story.append(Paragraph(_esc(FULL_LEGAL_DISCLAIMER_EN), disclaimer_style))
    else:
        story.append(Paragraph(_esc(FULL_LEGAL_DISCLAIMER_VI), disclaimer_style))

    story.append(Paragraph("Chart summary — deterministic", h2))
    story.append(
        Paragraph(
            _esc(f"he={report.chart_summary.he} · {report.chart_summary.lich_phap_summary}"),
            body,
        )
    )

    story.append(Paragraph("Patterns (vernacular first)", h2))
    if report.detected_patterns:
        for p in report.detected_patterns:
            vern = _vernacular_pattern_name(p.name)
            label = vern if vern == p.name else f"{vern} ({p.name})"
            story.append(
                Paragraph(
                    _esc(f"• {label} · polarity={p.polarity} · cung={p.cung or '—'}"),
                    body,
                )
            )
    else:
        story.append(Paragraph("No patterns listed.", body))

    story.append(Paragraph("AI interpretation", h2))
    story.append(Paragraph(_esc(report.interpretation.beginner or "—"), body))
    story.append(Paragraph(_esc(report.interpretation.expert or "—"), body))

    story.append(Paragraph("Recommendations", h2))
    for r in report.interpretation.recommendations:
        text = r if isinstance(r, str) else str(r)
        story.append(Paragraph(_esc(f"• {text}"), body))

    disc = report.ai_disclosure
    story.append(Paragraph("AIDisclosure", h2))
    story.append(
        Paragraph(
            _esc(
                f"model={disc.model} · limits={disc.limits} · "
                f"review_status={disc.review_status} · is_ai_generated=true"
            ),
            body,
        )
    )

    story.append(Paragraph("Citations", h2))
    for i, c in enumerate(report.citations, start=1):
        story.append(
            Paragraph(
                _esc(
                    f"{i}. {c.source} [{c.locator}] "
                    f"漢:{c.han or '—'} · BT:{c.bach_thoai or '—'} · D:{c.dich or '—'}"
                ),
                body,
            )
        )

    story.append(Spacer(1, 8))
    story.append(
        Paragraph(
            _esc("Educational decision support only — not fortune-telling."),
            body,
        )
    )

    doc.build(story)
    pdf = buf.getvalue()
    if not pdf.startswith(b"%PDF"):
        raise RuntimeError("reportlab produced non-PDF output")
    return pdf
