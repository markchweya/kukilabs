"""An in-process fake of the Ollama HTTP API for tests.

Tests register a responder per model output type; the fake inspects the JSON
schema Kuki sends (its "title" is the pydantic model name) and returns the
matching canned payload. This exercises the real request/response plumbing
without needing a model on the test machine.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from typing import Any

import httpx

Responder = Callable[[dict[str, Any]], Any]


class FakeOllama:
    def __init__(self, models: list[str] | None = None, embed_dim: int = 8):
        self.models = models if models is not None else ["llama3.2:3b", "nomic-embed-text:latest"]
        self.embed_dim = embed_dim
        self.responders: dict[str, Responder] = {}
        self.requests: list[tuple[str, dict[str, Any]]] = []
        self.down = False

    def respond(self, schema_title: str, responder: Responder | Any) -> None:
        """Register what to answer when Kuki asks for `schema_title` output."""
        self.responders[schema_title] = responder if callable(responder) else (lambda _req, v=responder: v)

    def transport(self) -> httpx.MockTransport:
        return httpx.MockTransport(self._handle)

    def _handle(self, request: httpx.Request) -> httpx.Response:
        if self.down:
            raise httpx.ConnectError("connection refused", request=request)
        body = json.loads(request.content or b"{}")
        self.requests.append((request.url.path, body))

        if request.url.path == "/api/tags":
            return httpx.Response(200, json={"models": [{"name": m} for m in self.models]})

        if request.url.path == "/api/embed":
            return httpx.Response(200, json={"embeddings": [self._embed(t) for t in body["input"]]})

        if request.url.path == "/api/chat":
            title = (body.get("format") or {}).get("title", "text")
            responder = self.responders.get(title)
            if responder is None:
                return httpx.Response(500, json={"error": f"no fake responder for {title}"})
            out = responder(body)
            content = out if isinstance(out, str) else json.dumps(out)
            return httpx.Response(200, json={"message": {"role": "assistant", "content": content}})

        return httpx.Response(404, json={"error": "unknown endpoint"})

    def _embed(self, text: str) -> list[float]:
        """Deterministic bag-of-letters vector: similar texts get similar vectors."""
        vec = [0.0] * self.embed_dim
        for ch in text.lower():
            if ch.isalpha():
                vec[ord(ch) % self.embed_dim] += 1.0
        return vec
