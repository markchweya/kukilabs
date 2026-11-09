"""Language-model access. Kuki only ever talks to a local Ollama server."""

from kuki.llm.ollama import OllamaClient, OllamaError, OllamaUnavailable

__all__ = ["OllamaClient", "OllamaError", "OllamaUnavailable"]
