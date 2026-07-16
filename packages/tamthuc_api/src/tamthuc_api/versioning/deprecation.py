"""Deprecation headers and route markers — TASK-API-002."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any


def deprecation_headers(
    replacement: str,
    sunset: str | datetime | None = None,
) -> dict[str, str]:
    """Build RFC 8594-style Deprecation / Link / Sunset headers."""
    headers = {
        "Deprecation": "true",
        "Link": f'<{replacement}>; rel="successor-version"',
    }
    if sunset is not None:
        if isinstance(sunset, datetime):
            if sunset.tzinfo is None:
                sunset = sunset.replace(tzinfo=UTC)
            # HTTP-date (IMF-fixdate)
            headers["Sunset"] = sunset.astimezone(UTC).strftime("%a, %d %b %Y %H:%M:%S GMT")
        else:
            headers["Sunset"] = str(sunset)
    return headers


@dataclass(frozen=True)
class DeprecatedRoute:
    """Metadata for a route retained ≥2–3 versions after deprecation."""

    path: str
    successor: str
    deprecated_in: int
    remove_in: int
    sunset: str | None = None

    def headers(self) -> dict[str, str]:
        return deprecation_headers(self.successor, self.sunset)

    def still_supported(self, current_major: int) -> bool:
        # retain for at least 2 versions after deprecation
        return current_major < self.remove_in and (self.remove_in - self.deprecated_in) >= 2


# Seed: example of a field/endpoint deprecation window (v1 still current).
DEPRECATED_CATALOG: list[DeprecatedRoute] = [
    DeprecatedRoute(
        path="/api/v1/knowledge/patterns",
        successor="/api/v2/knowledge/patterns",
        deprecated_in=1,
        remove_in=4,  # retained 3 majors after deprecation when v2 lands
        sunset="Wed, 08 Jul 2027 00:00:00 GMT",
    ),
]


def apply_deprecation_headers(response_headers: Any, path: str) -> None:
    for item in DEPRECATED_CATALOG:
        if path.rstrip("/") == item.path.rstrip("/") or path.startswith(item.path):
            for k, v in item.headers().items():
                response_headers[k] = v
            return
