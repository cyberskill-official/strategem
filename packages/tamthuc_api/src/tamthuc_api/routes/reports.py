from fastapi import APIRouter
from fastapi.responses import JSONResponse

from tamthuc_api.errors import error_envelope

router = APIRouter(tags=["reports"])


@router.post("/reports/generate")
def generate_report() -> JSONResponse:
    return JSONResponse(
        status_code=501,
        content=error_envelope("NOT_IMPLEMENTED", "REPORT-001 not mounted"),
    )


@router.get("/reports/{report_id}")
@router.get("/reports/{report_id}/download")
def get_report(report_id: str) -> JSONResponse:
    return JSONResponse(
        status_code=404,
        content=error_envelope("NOT_FOUND", f"report {report_id} not found"),
    )
