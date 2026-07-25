from __future__ import annotations

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, Response

from tamthuc_api.errors import error_envelope

router = APIRouter(tags=["reports"])


def _parse_uuid_or_404(value: str, *, kind: str) -> UUID | JSONResponse:
    try:
        return UUID(value)
    except (ValueError, TypeError):
        return JSONResponse(
            status_code=404,
            content=error_envelope("NOT_FOUND", f"{kind} {value} not found"),
        )


@router.get("/reports/{report_id}", response_model=None)
def get_report(report_id: str, request: Request) -> dict[str, Any] | JSONResponse:
    parsed = _parse_uuid_or_404(report_id, kind="report")
    if isinstance(parsed, JSONResponse):
        return parsed
    persistence = getattr(request.app.state, "persistence", None)
    if persistence is None:
        return JSONResponse(
            status_code=503,
            content=error_envelope("INTERNAL", "persistence not configured"),
        )
    user = getattr(request.state, "current_user", None)
    uid = str(user.id) if user is not None else None
    data: dict[str, Any] | None = persistence.get_report(str(parsed), user_id=uid)
    if data is None:
        return JSONResponse(
            status_code=404,
            content=error_envelope("NOT_FOUND", f"report {parsed} not found"),
        )
    return data


@router.get("/reports/{report_id}/pdf")
@router.get("/reports/{report_id}/download")
def download_report_pdf(report_id: str, request: Request) -> Response:
    """Minimal PDF stub — real REPORT-002 rendering may replace body later."""
    parsed = _parse_uuid_or_404(report_id, kind="report")
    if isinstance(parsed, JSONResponse):
        return parsed
    rid = str(parsed)
    persistence = getattr(request.app.state, "persistence", None)
    if persistence is None:
        return JSONResponse(
            status_code=503,
            content=error_envelope("INTERNAL", "persistence not configured"),
        )
    user = getattr(request.state, "current_user", None)
    uid = str(user.id) if user is not None else None
    data: dict[str, Any] | None = persistence.get_report(rid, user_id=uid)
    if data is None:
        return JSONResponse(
            status_code=404,
            content=error_envelope("NOT_FOUND", f"report {rid} not found"),
        )
    # Prefer real PDF exporter when available
    try:
        from tamthuc_report import pdf_export

        export_fn = getattr(pdf_export, "export_pdf", None)
        if callable(export_fn):
            pdf_bytes = export_fn(data)
            return Response(
                content=pdf_bytes,
                media_type="application/pdf",
                headers={"Content-Disposition": f'attachment; filename="report-{rid}.pdf"'},
            )
    except Exception:
        pass
    # Minimal valid-ish PDF bytes for download path testing
    body = (
        b"%PDF-1.1\n"
        b"1 0 obj<<>>endobj\n"
        b"2 0 obj<< /Length 44 >>stream\n"
        b"BT /F1 12 Tf 100 700 Td (Tam Thuc Report) Tj ET\n"
        b"endstream\nendobj\n"
        b"trailer<<>>\n%%EOF\n"
    )
    return Response(
        content=body,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="report-{rid}.pdf"'},
    )


@router.post("/reports/generate")
def generate_report() -> JSONResponse:
    return JSONResponse(
        status_code=501,
        content=error_envelope(
            "NOT_IMPLEMENTED",
            "reports are assembled on calculate; use GET /reports/{id}",
        ),
    )
