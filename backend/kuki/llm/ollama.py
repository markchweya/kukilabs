"""A small, dependency-light client for the Ollama HTTP API.

We talk to Ollama directly over HTTP instead of using an SDK so that the
surface we depend on is tiny and easy to mock in tests:

    GET  /api/tags   list installed models
    POST /api/chat   chat completion (optionally constrained to a JSON schema)
    POST /api/embed  batch embeddings
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import httpx

Message = dict[str, str]


class OllamaError(RuntimeError):
    """Ollama answered, but not with something we could use."""


class OllamaUnavailable(OllamaError):
    """Ollama is not running or not reachable."""


@dataclass(frozen=True)
class ModelStatus:
    reachable: bool
    installed: list[str]

    def has(self, model: str) -> bool:
        """True if `model` is installed. "llama3.2" also matches "llama3.2:latest"."""
        wanted = model if ":" in model else f"{model}:latest"
        return any(name in (model, wanted) for name in self.installed)


class OllamaClient:
    def __init__(self, host: str, timeout: float = 300, transport: httpx.BaseTransport | None = None):
        # A custom transport lets tests swap in httpx.MockTransport.
        self._http = httpx.Client(base_url=host, timeout=timeout, transport=transport)

    def close(self) -> None:
        self._http.close()

    def status(self) -> ModelStatus:
        """Report whether Ollama is up and which models are installed.

        Uses a short timeout: this backs the UI's status pill and must never
        hang the page.
        """
        try:
            res = self._http.get("/api/tags", timeout=3)
            res.raise_for_status()
        except httpx.HTTPError:
            return ModelStatus(reachable=False, installed=[])
        names = [m.get("name", "") for m in res.json().get("models", [])]
        return ModelStatus(reachable=True, installed=[n for n in names if n])

    def chat(
        self,
        model: str,
        messages: list[Message],
        *,
        schema: dict[str, Any] | None = None,
        temperature: float = 0.2,
        num_ctx: int = 8192,
    ) -> str:
        """Run one non-streaming chat completion and return the reply text.

        When `schema` is given, Ollama constrains decoding to that JSON schema
        (structured outputs, Ollama >= 0.5), which makes small local models far
        more reliable at producing parseable JSON.
        """
        payload: dict[str, Any] = {
            "model": model,
            "messages": messages,
            "stream": False,
            "options": {"temperature": temperature, "num_ctx": num_ctx},
        }
        if schema is not None:
            payload["format"] = schema
        data = self._post("/api/chat", payload)
        content = (data.get("message") or {}).get("content")
        if not isinstance(content, str):
            raise OllamaError("Ollama returned a chat response without message content.")
        return content.strip()

    def _post(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        """POST JSON and translate transport failures into Kuki's error types."""
        try:
            res = self._http.post(path, json=payload)
        except httpx.ConnectError as exc:
            raise OllamaUnavailable("Ollama is not running. Start it with `ollama serve`.") from exc
        except httpx.TimeoutException as exc:
            raise OllamaError("The local model took too long to answer.") from exc
        if res.status_code == 404:
            # Ollama uses 404 for "model not pulled".
            raise OllamaError(_error_text(res) or "Model not found. Pull it with `ollama pull`.")
        if res.is_error:
            raise OllamaError(_error_text(res) or f"Ollama error {res.status_code}")
        return res.json()


def _error_text(res: httpx.Response) -> str:
    try:
        return str(res.json().get("error", ""))
    except ValueError:
        return res.text[:200]
