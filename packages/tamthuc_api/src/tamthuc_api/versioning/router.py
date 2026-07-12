"""URL-primary API versioning — FR-API-002."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

from tamthuc_api.errors import error_envelope
from tamthuc_api.versioning.deprecation import apply_deprecation_headers

CURRENT_MAJOR = 1
SUPPORTED_MAJORS: frozenset[int] = frozenset({1})
VERSION_HEADER = "X-API-Version"


def effective_version(
    url_version: int | None,
    header_version: int | None,
) -> int | None:
    """URL wins when both present; either alone is accepted."""
    if url_version is not None:
        return url_version
    return header_version


def parse_header_version(value: str | None) -> int | None:
    if value is None or value.strip() == "":
        return None
    try:
        return int(value.strip().lstrip("vV"))
    except ValueError:
        return None


def mount_versioned(
    app: FastAPI, router: APIRouter, *, majors: frozenset[int] | None = None
) -> None:
    """Mount a router under /api/v{n} for each supported major."""
    for major in sorted(majors or SUPPORTED_MAJORS):
        app.include_router(router, prefix=f"/api/v{major}")


class VersioningMiddleware(BaseHTTPMiddleware):
    """Resolve effective API version; reject unknown; attach deprecation headers."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        path = request.url.path
        url_ver: int | None = None
        parts = path.strip("/").split("/")
        # expect api / vN / ...
        if len(parts) >= 2 and parts[0] == "api" and parts[1].startswith("v"):
            try:
                url_ver = int(parts[1][1:])
            except ValueError:
                url_ver = None
            if url_ver is not None and url_ver not in SUPPORTED_MAJORS:
                return JSONResponse(
                    status_code=404,
                    content=error_envelope(
                        "NOT_FOUND",
                        f"unsupported API version v{url_ver}; supported={sorted(SUPPORTED_MAJORS)}",
                    ),
                )

        hdr = parse_header_version(request.headers.get(VERSION_HEADER))
        if url_ver is None and hdr is not None and hdr not in SUPPORTED_MAJORS:
            return JSONResponse(
                status_code=404,
                content=error_envelope(
                    "NOT_FOUND",
                    f"unsupported API version v{hdr}; supported={sorted(SUPPORTED_MAJORS)}",
                ),
            )

        eff = effective_version(url_ver, hdr)
        request.state.api_version = eff if eff is not None else CURRENT_MAJOR

        response = await call_next(request)
        apply_deprecation_headers(response.headers, path)
        # expose which version served the request
        response.headers["X-API-Version"] = str(request.state.api_version)
        return response


def calculation_stability_note() -> dict[str, Any]:
    """Document the calc-stable / interpretation-variable invariant."""
    return {
        "calculation_output": {
            "stability": "stable",
            "changes_via": "FR-PLAT-002 envelope_version bump + migration note only",
        },
        "interpretation": {
            "stability": "variable",
            "note": "RAG-003 prose may improve across versions; not byte-stable",
        },
    }
