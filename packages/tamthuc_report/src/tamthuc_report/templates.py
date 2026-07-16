"""Question-type report templates — TASK-REPORT-003 (read-only presentation)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict

from tamthuc_report.models import StructuredReport

TEMPLATE_DIR = Path(__file__).parent / "templates" / "question_types"


class ReportTemplate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    question_type: str
    he: list[str]
    dung_than_focus: str
    section_order: list[str]
    sample_path: str


class Section(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str
    label: str
    content: Any


_TEMPLATES: dict[str, ReportTemplate] = {
    "trach_thoi": ReportTemplate(
        question_type="trach_thoi",
        he=["ky_mon", "luc_nham"],
        dung_than_focus="the matter + the chosen hour",
        section_order=[
            "chart_summary",
            "detected_patterns",
            "recommendations",
            "interpretation",
            "citations",
            "confidence",
        ],
        sample_path=str(TEMPLATE_DIR / "trach_thoi.md"),
    ),
    "phuong_vi": ReportTemplate(
        question_type="phuong_vi",
        he=["ky_mon"],
        dung_than_focus="the direction palace",
        section_order=[
            "chart_summary",
            "detected_patterns",
            "interpretation",
            "recommendations",
            "citations",
            "confidence",
        ],
        sample_path=str(TEMPLATE_DIR / "phuong_vi.md"),
    ),
    "chu_khach": ReportTemplate(
        question_type="chu_khach",
        he=["thai_at", "ky_mon", "luc_nham"],
        dung_than_focus="self (chu) + other (khach)",
        section_order=[
            "interpretation",
            "detected_patterns",
            "chart_summary",
            "recommendations",
            "citations",
            "confidence",
        ],
        sample_path=str(TEMPLATE_DIR / "chu_khach.md"),
    ),
    "vi_mo": ReportTemplate(
        question_type="vi_mo",
        he=["thai_at"],
        dung_than_focus="the trend / cycle",
        section_order=[
            "chart_summary",
            "interpretation",
            "detected_patterns",
            "recommendations",
            "citations",
            "confidence",
        ],
        sample_path=str(TEMPLATE_DIR / "vi_mo.md"),
    ),
}

_DEFAULT = ReportTemplate(
    question_type="default",
    he=["ky_mon"],
    dung_than_focus="general",
    section_order=[
        "chart_summary",
        "detected_patterns",
        "interpretation",
        "recommendations",
        "citations",
        "confidence",
    ],
    sample_path="",
)

# aliases
_ALIASES = {
    "timing": "trach_thoi",
    "direction": "phuong_vi",
    "competitor": "chu_khach",
    "risk": "chu_khach",
    "macro": "vi_mo",
}


def template_for(loai_cau_hoi: str) -> ReportTemplate:
    key = (loai_cau_hoi or "").strip().lower()
    key = _ALIASES.get(key, key)
    return _TEMPLATES.get(key, _DEFAULT)


def render_sections(report: StructuredReport, template: ReportTemplate) -> list[Section]:
    """Reorder/label existing sections only — never mutates the report."""
    bucket: dict[str, Any] = {
        "chart_summary": report.chart_summary.model_dump(),
        "detected_patterns": [p.model_dump() for p in report.detected_patterns],
        "interpretation": report.interpretation.model_dump(),
        "recommendations": list(report.interpretation.recommendations),
        "citations": [c.model_dump() for c in report.citations],
        "confidence": report.confidence,
    }
    labels = {
        "chart_summary": "Chart summary",
        "detected_patterns": "Detected patterns",
        "interpretation": "Interpretation",
        "recommendations": "Recommendations",
        "citations": "Citations",
        "confidence": "Confidence",
    }
    return [
        Section(id=sid, label=labels.get(sid, sid), content=bucket[sid])
        for sid in template.section_order
        if sid in bucket
    ]
