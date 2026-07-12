from __future__ import annotations

import json
import re
from typing import Any

_REDACT_KEYS = frozenset({"birth_data", "password", "question", "question_text"})


def redact(obj: Any) -> Any:
    if isinstance(obj, dict):
        out = {}
        for k, v in obj.items():
            if k.lower() in _REDACT_KEYS or "birth" in k.lower():
                out[k] = "[REDACTED]"
            else:
                out[k] = redact(v)
        return out
    if isinstance(obj, list):
        return [redact(x) for x in obj]
    if isinstance(obj, str):
        # strip obvious ISO birth dates in free text
        return re.sub(r"\b\d{4}-\d{2}-\d{2}\b", "[DATE]", obj)
    return obj


def structured_log(event: str, *, request_id: str, **fields: Any) -> str:
    payload = redact({"event": event, "request_id": request_id, **fields})
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)
