from __future__ import annotations

from dataclasses import dataclass
import json
import os
from pathlib import Path
from typing import Any
from urllib.error import URLError
from urllib.request import Request, urlopen

from dotenv import load_dotenv


REPO_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(REPO_ROOT / ".env.local")


DEFAULT_MODEL_ORDER = (
    "llama3.2:3b",
    "gemma3:4b",
    "mistral:latest",
    "llama3:latest",
    "gemma4:latest",
)


@dataclass(frozen=True)
class AIStatus:
    ready: bool
    provider: str
    model: str
    message: str


def _ollama_base_url() -> str:
    return os.getenv("OLLAMA_HOST", "http://localhost:11434").rstrip("/")


def _request_json(path: str, payload: dict[str, Any] | None = None, timeout: int = 120) -> dict[str, Any]:
    url = f"{_ollama_base_url()}{path}"
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    request = Request(url, data=body, headers={"Content-Type": "application/json"})
    with urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def list_models() -> list[str]:
    try:
        data = _request_json("/api/tags", timeout=5)
    except (OSError, URLError, TimeoutError, json.JSONDecodeError):
        return []

    return [item.get("name", "") for item in data.get("models", []) if item.get("name")]


def choose_model() -> str:
    configured = os.getenv("KUKI_AI_MODEL", "").strip()
    models = list_models()
    if configured:
        return configured
    for candidate in DEFAULT_MODEL_ORDER:
        if candidate in models:
            return candidate
    return models[0] if models else DEFAULT_MODEL_ORDER[0]


def get_ai_status() -> AIStatus:
    models = list_models()
    if not models:
        return AIStatus(
            ready=False,
            provider="Ollama",
            model="",
            message="AI is offline. Start Ollama, then refresh Kuki.",
        )

    model = choose_model()
    if model not in models:
        return AIStatus(
            ready=False,
            provider="Ollama",
            model=model,
            message=f"Model '{model}' is not installed in Ollama.",
        )

    return AIStatus(
        ready=True,
        provider="Ollama",
        model=model,
        message=f"Ready with {model}.",
    )


def generate_ai_reply(*, system_prompt: str, user_prompt: str, model: str | None = None) -> str:
    selected_model = model or choose_model()
    payload = {
        "model": selected_model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "stream": False,
        "options": {
            "temperature": 0.35,
            "num_ctx": 4096,
        },
    }
    data = _request_json("/api/chat", payload=payload, timeout=180)
    message = data.get("message") or {}
    return (message.get("content") or "").strip()
