"""A small, dependency-light client for the Ollama HTTP API.

We talk to Ollama directly over HTTP instead of using an SDK so that the
surface we depend on is tiny and easy to mock in tests:

    GET  /api/tags   list installed models
    POST /api/chat   chat completion (optionally constrained to a JSON schema)
    POST /api/embed  batch embeddings
"""

from __future__ import annotations

from dataclasses import dataclass

import httpx


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
