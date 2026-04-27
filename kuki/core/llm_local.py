from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from importlib.util import find_spec
from pathlib import Path

from kuki.core.config import get_settings


class LocalLLMError(RuntimeError):
    pass


@dataclass(frozen=True)
class LocalModelStatus:
    ready: bool
    backend: str
    model_path: str
    message: str
    threads: int


def get_local_model_status(model_path: Path | None = None) -> LocalModelStatus:
    settings = get_settings()
    resolved_path = (model_path or settings.llm_model_path).resolve()

    if not resolved_path.exists():
        return LocalModelStatus(
            ready=False,
            backend="llama.cpp",
            model_path=str(resolved_path),
            message="No GGUF model found yet. Add a local model file to models/llm and point LLM_MODEL_PATH to it.",
            threads=settings.llm_n_threads,
        )

    if find_spec("llama_cpp") is None:
        return LocalModelStatus(
            ready=False,
            backend="llama.cpp",
            model_path=str(resolved_path),
            message="llama-cpp-python is not installed in this environment.",
            threads=settings.llm_n_threads,
        )

    return LocalModelStatus(
        ready=True,
        backend="llama.cpp",
        model_path=str(resolved_path),
        message="Local CPU model is ready.",
        threads=settings.llm_n_threads,
    )


@lru_cache(maxsize=2)
def _load_llama(model_path: str, n_ctx: int, n_threads: int):
    from llama_cpp import Llama

    return Llama(
        model_path=model_path,
        n_ctx=n_ctx,
        n_threads=n_threads,
        n_gpu_layers=0,
        verbose=False,
    )


class LocalLLM:
    def __init__(self, model_path: Path | None = None):
        self.settings = get_settings()
        self.model_path = (model_path or self.settings.llm_model_path).resolve()
        status = get_local_model_status(self.model_path)
        if not status.ready:
            raise LocalLLMError(status.message)

        self.llm = _load_llama(
            str(self.model_path),
            self.settings.llm_n_ctx,
            self.settings.llm_n_threads,
        )

    def generate(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int | None = None,
        temperature: float = 0.25,
    ) -> str:
        prompt = (
            "<|system|>\n"
            f"{system_prompt.strip()}\n"
            "<|user|>\n"
            f"{user_prompt.strip()}\n"
            "<|assistant|>\n"
        )
        result = self.llm(
            prompt,
            max_tokens=max_tokens or self.settings.llm_max_tokens,
            temperature=temperature,
            repeat_penalty=1.08,
            stop=["<|user|>", "<|system|>"],
        )
        return (result["choices"][0]["text"] or "").strip()
