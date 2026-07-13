from __future__ import annotations

import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import pytest
from tamthuc_rag.llm import OpenAICompatibleLlm, StubLlm, llm_from_env


class _Handler(BaseHTTPRequestHandler):
    def do_POST(self) -> None:  # noqa: N802
        length = int(self.headers.get("Content-Length", "0"))
        _ = self.rfile.read(length)
        body = {
            "choices": [
                {
                    "message": {
                        "content": json.dumps(
                            {
                                "beginner": "Local beginner note",
                                "expert": "Local expert note",
                                "recommendations": [
                                    {"text": "Study patterns", "citations": ["c1"]}
                                ],
                            }
                        )
                    }
                }
            ]
        }
        raw = json.dumps(body).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def log_message(self, format: str, *args: object) -> None:  # noqa: A003
        return


def test_openai_compatible_chat_completions_contract() -> None:
    server = HTTPServer(("127.0.0.1", 0), _Handler)
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        client = OpenAICompatibleLlm(
            base_url=f"http://127.0.0.1:{port}/v1",
            model="test-model",
            api_key="",
            timeout_s=5,
        )
        out = client.complete("prompt with - yba_1: unit")
        assert out["beginner"] == "Local beginner note"
        assert out["expert"] == "Local expert note"
        assert out["recommendations"][0]["citations"] == ["c1"]
        assert client.model == "test-model"
    finally:
        server.shutdown()


def test_openai_compatible_unreachable() -> None:
    client = OpenAICompatibleLlm(
        base_url="http://127.0.0.1:1/v1",
        model="x",
        timeout_s=1,
    )
    try:
        client.complete("hi")
        raise AssertionError("expected RuntimeError")
    except RuntimeError as e:
        assert "llm_unreachable" in str(e) or "llm_http" in str(e) or "llm_timeout" in str(e)


def test_llm_from_env_stub_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("LLM_BACKEND", raising=False)
    assert isinstance(llm_from_env(), StubLlm)


def test_llm_from_env_openai(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LLM_BACKEND", "lmstudio")
    monkeypatch.setenv("LLM_BASE_URL", "http://127.0.0.1:1234/v1")
    client = llm_from_env()
    assert isinstance(client, OpenAICompatibleLlm)
