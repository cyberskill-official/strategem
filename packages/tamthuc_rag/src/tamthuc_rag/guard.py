from __future__ import annotations

import re
from typing import Any

_FORBIDDEN = re.compile(
    r"(?i)\b(you will definitely|chắc chắn sẽ|diagnose|prescribe|đầu tư ngay|sue|kiện tụng|"
    r"cure cancer|chữa ung thư|guaranteed profit)\b"
)


def strip_unknown_citations(
    recommendations: list[dict[str, Any]], allowed: set[str]
) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for rec in recommendations:
        cites = [c for c in rec.get("citations") or [] if c in allowed]
        if not cites:
            continue  # citation-required
        rec = dict(rec)
        rec["citations"] = cites
        # drop claims that invent ids in text? keep body if cites ok
        out.append(rec)
    return out


def framing_ok(text: str) -> bool:
    return _FORBIDDEN.search(text) is None
