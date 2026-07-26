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


def _parse_retrieved_sources(prompt: str) -> list[tuple[str, str]]:
    """Extract (citation_id, layer_text) pairs from the retrieval section of the prompt."""
    sources: list[tuple[str, str]] = []
    in_section = False
    for line in prompt.splitlines():
        if line.strip().startswith("## Retrieved"):
            in_section = True
            continue
        if in_section and line.startswith("## "):
            break
        if not in_section:
            continue
        if line.startswith("- ") and ":" in line:
            body = line[2:]
            cid, rest = body.split(":", 1)
            sources.append((cid.strip(), rest.strip()))
    return sources


def _he_from_prompt(prompt: str) -> str:
    m = re.search(r"['\"]he['\"]\s*:\s*['\"]([^'\"]+)['\"]", prompt)
    return m.group(1) if m else "classical chart"


class StubLlm:
    """Deterministic CI stub — grounded prose from retrieved classical chunks."""

    model = "stub-llm-grounded"

    def complete(self, prompt: str) -> dict[str, Any]:
        sources = _parse_retrieved_sources(prompt)
        cites = [c for c, _ in sources]
        he = _he_from_prompt(prompt)

        if not sources:
            return {
                "beginner": (
                    f"Educational reading for {he}: no classical units were retrieved. "
                    "No free-memory claims are offered."
                ),
                "expert": "Empty retrieval set; refuse uncited interpretation.",
                "recommendations": [],
            }

        # Build substantive, citation-grounded readings from chunk text (not generic filler).
        excerpts: list[str] = []
        for cid, text in sources[:5]:
            cleaned = text.strip("[]'\" ")
            if cleaned:
                excerpts.append(f"{cid}: {cleaned}")

        joined = "; ".join(excerpts[:3])
        beginner = (
            f"Educational reading for {he}. Retrieved classical guidance includes: {joined}. "
            "Treat this as cultural decision-support — you decide how it applies to your situation."
        )
        expert = (
            f"Technical notes for {he} grounded in {len(sources)} retrieved unit(s). "
            f"Primary sources: {', '.join(cites[:4])}. "
            f"Layer cues — {joined}. "
            "Cross-check polarity and timing against the stamped engine chart; "
            "do not treat this as prophecy or a guaranteed outcome."
        )
        first_cite = cites[:2] or []
        return {
            "beginner": beginner,
            "expert": expert,
            "recommendations": [
                {
                    "text": (
                        "Weigh the cited classical units against your real-world constraints "
                        f"({', '.join(first_cite) or 'local corpus'})."
                    ),
                    "citations": first_cite,
                },
                {
                    "text": "Prefer engine-stamped patterns plus cited glosses over free memory.",
                    "citations": cites[1:3] or first_cite,
                },
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
                        "Ground every claim in the retrieved sources. "
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
        try:
            return _parse_structured(content)
        except (json.JSONDecodeError, RuntimeError):
            # Local / Workers AI models often return prose or near-JSON; keep
            # the educational path live instead of forcing rule-based fallback.
            text = content.strip() or "Educational reading from local model."
            return {
                "beginner": text,
                "expert": text,
                "recommendations": [
                    {"text": "Review cited classical units carefully.", "citations": []}
                ],
            }


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


def llm_from_env(
    *,
    backend: str | None = None,
    base_url: str | None = None,
    model: str | None = None,
    api_key: str | None = None,
) -> LlmClient:
    """Factory: LLM_BACKEND=openai_compatible|stub|off (default stub).

    Callers (e.g. API operator BYOK) may override backend/base_url/model/api_key.
    Resolution order at the API layer: operator settings → env → stub.
    """
    chosen = (backend or os.environ.get("LLM_BACKEND") or "stub").strip().lower()
    if chosen in {"openai_compatible", "openai", "lmstudio", "local"}:
        return OpenAICompatibleLlm(base_url=base_url, model=model, api_key=api_key)
    if chosen in {"off", "none", "disabled"}:
        return StubLlm()
    return StubLlm()
