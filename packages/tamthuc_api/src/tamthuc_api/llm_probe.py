"""LLM / LM Studio readiness probe (Phase 4)."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any


def probe_llm() -> dict[str, Any]:
    """Probe configured OpenAI-compatible backend (does not send completions)."""
    backend = (os.environ.get("LLM_BACKEND") or "stub").strip().lower()
    base = (os.environ.get("LLM_BASE_URL") or "http://127.0.0.1:1234/v1").rstrip("/")
    model = (os.environ.get("LLM_MODEL") or "local-model").strip()
    out: dict[str, Any] = {
        "llm_backend": backend,
        "llm_base_url": base,
        "llm_model": model,
        "llm_reachable": False,
        "llm_models_sample": [],
        "llm_model_listed": False,
        "degraded_ok": True,
    }
    if backend in {"stub", "off", "none", "disabled"}:
        out["llm_reachable"] = True
        out["note"] = "stub/off backend — no network probe"
        return out

    url = f"{base}/models"
    api_key = (os.environ.get("LLM_API_KEY") or "").strip()
    headers = {"Accept": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    req = urllib.request.Request(url, headers=headers, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=3) as resp:
            raw = resp.read().decode("utf-8")
        payload = json.loads(raw)
        data = payload.get("data") if isinstance(payload, dict) else None
        ids: list[str] = []
        if isinstance(data, list):
            for item in data[:12]:
                if isinstance(item, dict) and item.get("id"):
                    ids.append(str(item["id"]))
        out["llm_reachable"] = True
        out["llm_models_sample"] = ids
        out["llm_model_listed"] = model in ids if ids else True
    except (
        urllib.error.URLError,
        urllib.error.HTTPError,
        TimeoutError,
        json.JSONDecodeError,
        OSError,
    ) as e:
        out["llm_reachable"] = False
        out["error"] = type(e).__name__
        out["degraded_ok"] = True
    return out
