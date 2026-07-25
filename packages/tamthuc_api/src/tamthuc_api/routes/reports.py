from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, Response

from tamthuc_api.errors import error_envelope

router = APIRouter(tags=["reports"])


@router.get("/reports/{report_id}", response_model=None)
def get_report(report_id: str, request: Request) -> dict[str, Any] | JSONResponse:
    persistence = getattr(request.app.state, "persistence", None)
    if persistence is None:
        return JSONResponse(
            status_code=503,
            content=error_envelope("INTERNAL", "persistence not configured"),
        )
    data: dict[str, Any] | None = persistence.get_report(report_id)
    if data is None:
        return JSONResponse(
            status_code=404,
            content=error_envelope("NOT_FOUND", f"report {report_id} not found"),
        )
    return data


@router.get("/reports/{report_id}/pdf")
@router.get("/reports/{report_id}/download")
def download_report_pdf(report_id: str, request: Request) -> Response:
    """PDF download — report_id may be report UUID or cast query_id."""
    persistence = getattr(request.app.state, "persistence", None)
    if persistence is None:
        return JSONResponse(
            status_code=503,
            content=error_envelope("INTERNAL", "persistence not configured"),
        )
    data: dict[str, Any] | None = persistence.get_report(report_id)
    if data is None:
        return JSONResponse(
            status_code=404,
            content=error_envelope("NOT_FOUND", f"report {report_id} not found"),
        )
    try:
        from tamthuc_report import pdf_export

        export_fn = getattr(pdf_export, "export_pdf", None)
        if callable(export_fn):
            pdf_bytes = export_fn(data)
            if isinstance(pdf_bytes, (bytes, bytearray)) and pdf_bytes.startswith(b"%PDF"):
                return Response(
                    content=bytes(pdf_bytes),
                    media_type="application/pdf",
                    headers={
                        "Content-Disposition": f'attachment; filename="report-{report_id}.pdf"'
                    },
                )
    except Exception:
        pass
    return JSONResponse(
        status_code=500,
        content=error_envelope("INTERNAL", "pdf export failed"),
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
