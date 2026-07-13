from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request
from typing import Any, Protocol


class LlmClient(Protocol):
    model: str

    def complete(self, prompt: str) -> dict[str, Any]: ...


class StubLlm:
    """Deterministic stub for CI — no network."""

    model = "stub-llm"

    def complete(self, prompt: str) -> dict[str, Any]:
        # Extract first citation id if present
        cites: list[str] = []
        for line in prompt.splitlines():
            if line.startswith("- ") and ":" in line:
                cites.append(line[2:].split(":", 1)[0].strip())
        return {
            "beginner": "A cautious educational reading of the chart patterns.",
            "expert": "Technical notes grounded in the retrieved classical units.",
            "recommendations": [
                {
                    "text": "Reflect on timing using the cited classical guidance.",
                    "citations": cites[:1] or [],
                }
            ],
        }


class OpenAICompatibleLlm:
    """HTTP client for OpenAI-compatible /chat/completions (LMStudio, etc.).

    Env (see docs/deploy/local-docker-lmstudio.md):
      LLM_BASE_URL   default http://127.0.0.1:1234/v1
      LLM_MODEL      default local-model
      LLM_API_KEY    optional (LMStudio often empty)
      LLM_TIMEOUT_S  default 60
    """

    def __init__(
        self,
        *,
        base_url: str | None = None,
        model: str | None = None,
        api_key: str | None = None,
        timeout_s: float | None = None,
    ) -> None:
        self.base_url = (
            base_url or os.environ.get("LLM_BASE_URL") or "http://127.0.0.1:1234/v1"
        ).rstrip("/")
        self.model = model or os.environ.get("LLM_MODEL") or "local-model"
        self.api_key = (
            api_key
            if api_key is not None
            else os.environ.get("LLM_API_KEY") or os.environ.get("OPENAI_API_KEY", "")
        )
        self.timeout_s = float(
            timeout_s if timeout_s is not None else os.environ.get("LLM_TIMEOUT_S") or "60"
        )

    def complete(self, prompt: str) -> dict[str, Any]:
        url = f"{self.base_url}/chat/completions"
        body = {
            "model": self.model,
            "temperature": 0.2,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You interpret classical chart patterns for education only. "
                        "Respond with a single JSON object keys: beginner (str), expert (str), "
                        "recommendations (array of {text, citations: string[]}). "
                        "No medical/legal/financial verdicts. No destiny claims."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            "response_format": {"type": "json_object"},
        }
        data = json.dumps(body).encode("utf-8")
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=self.timeout_s) as resp:
                raw = resp.read().decode("utf-8")
        except urllib.error.HTTPError as e:
            detail = e.read().decode("utf-8", errors="replace") if e.fp else str(e)
            raise RuntimeError(f"llm_http_{e.code}: {detail[:500]}") from e
        except urllib.error.URLError as e:
            raise RuntimeError(f"llm_unreachable: {e.reason}") from e
        except TimeoutError as e:
            raise RuntimeError("llm_timeout") from e

        payload = json.loads(raw)
        content = _extract_message_content(payload)
        return _parse_structured(content)


def _extract_message_content(payload: dict[str, Any]) -> str:
    choices = payload.get("choices") or []
    if not choices:
        raise RuntimeError("llm_empty_choices")
    msg = choices[0].get("message") or {}
    content = msg.get("content")
    if not isinstance(content, str) or not content.strip():
        raise RuntimeError("llm_empty_content")
    return content


def _parse_structured(content: str) -> dict[str, Any]:
    text = content.strip()
    # Strip markdown fences if the local model wraps JSON.
    fence = re.match(r"^```(?:json)?\s*([\s\S]*?)\s*```$", text, re.IGNORECASE)
    if fence:
        text = fence.group(1).strip()
    try:
        obj = json.loads(text)
    except json.JSONDecodeError:
        # Best-effort: first {...} block
        start = text.find("{")
        end = text.rfind("}")
        if start >= 0 and end > start:
            obj = json.loads(text[start : end + 1])
        else:
            raise RuntimeError("llm_invalid_json") from None
    if not isinstance(obj, dict):
        raise RuntimeError("llm_not_object")
    beginner = str(obj.get("beginner") or obj.get("beginner_interpretation") or "")
    expert = str(obj.get("expert") or obj.get("expert_interpretation") or "")
    recs_in = obj.get("recommendations") or []
    recommendations: list[dict[str, Any]] = []
    if isinstance(recs_in, list):
        for r in recs_in:
            if not isinstance(r, dict):
                continue
            citations = r.get("citations") or []
            if not isinstance(citations, list):
                citations = []
            recommendations.append(
                {
                    "text": str(r.get("text") or ""),
                    "citations": [str(c) for c in citations],
                }
            )
    return {
        "beginner": beginner or "Educational reading from local model.",
        "expert": expert or "Technical notes from local model.",
        "recommendations": recommendations
        or [{"text": "Review cited classical units carefully.", "citations": []}],
    }


def llm_from_env() -> LlmClient:
    """Factory: LLM_BACKEND=openai_compatible|stub|off (default stub)."""
    backend = (os.environ.get("LLM_BACKEND") or "stub").strip().lower()
    if backend in {"openai_compatible", "openai", "lmstudio", "local"}:
        return OpenAICompatibleLlm()
    if backend in {"off", "none", "disabled"}:
        return StubLlm()
    return StubLlm()
