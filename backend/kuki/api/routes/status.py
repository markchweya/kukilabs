"""GET /api/status: is everything Kuki needs available on this machine?

Powers the status pill in the UI and the first-run setup checklist, so every
missing piece comes with the exact command that fixes it.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from kuki import __version__
from kuki.api.deps import get_llm, get_settings
from kuki.config import Settings
from kuki.ingest.audio import whisper_available
from kuki.ingest.image import ocr_available
from kuki.llm import OllamaClient

router = APIRouter()


class Check(BaseModel):
    ok: bool
    label: str
    detail: str
    fix: str | None = None


class Status(BaseModel):
    version: str
    ai_ready: bool
    chat_model: str
    embed_model: str
    checks: dict[str, Check]


@router.get("/api/status", response_model=Status)
def status(settings: Settings = Depends(get_settings), llm: OllamaClient = Depends(get_llm)) -> Status:
    models = llm.status()
    chat_ok = models.reachable and models.has(settings.chat_model)
    embed_ok = models.reachable and models.has(settings.embed_model)

    checks = {
        "ollama": Check(
            ok=models.reachable,
            label="Ollama",
            detail="Running" if models.reachable else "Not running",
            fix=None if models.reachable else "Install from ollama.com, then run: ollama serve",
        ),
        "chat_model": Check(
            ok=chat_ok,
            label="Study model",
            detail=settings.chat_model + (" installed" if chat_ok else " not installed"),
            fix=None if chat_ok else f"ollama pull {settings.chat_model}",
        ),
        "embed_model": Check(
            ok=embed_ok,
            label="Search model (optional)",
            detail=settings.embed_model + (" installed" if embed_ok else " not installed; using keyword search"),
            fix=None if embed_ok else f"ollama pull {settings.embed_model}",
        ),
        "ocr": Check(
            ok=ocr_available(),
            label="Photo reading (optional)",
            detail="Ready" if ocr_available() else "Not installed",
            fix=None if ocr_available() else "pip install rapidocr-onnxruntime",
        ),
        "whisper": Check(
            ok=whisper_available(),
            label="Recording transcription (optional)",
            detail="Ready" if whisper_available() else "Not installed",
            fix=None if whisper_available() else "pip install faster-whisper",
        ),
    }
    return Status(
        version=__version__,
        ai_ready=chat_ok,
        chat_model=settings.chat_model,
        embed_model=settings.embed_model,
        checks=checks,
    )
