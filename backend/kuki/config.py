"""Runtime configuration.

All settings come from environment variables so Kuki can be configured without
touching code. Defaults are chosen to "just work" on a student laptop running
Ollama with the two recommended models pulled.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path


def _env_int(name: str, default: int, minimum: int = 1) -> int:
    """Read an integer env var, falling back to the default on bad input.

    A typo in an env var should never crash the app on startup, so invalid
    values are ignored rather than raised.
    """
    raw = os.getenv(name)
    if raw is None or not raw.strip():
        return default
    try:
        return max(minimum, int(raw))
    except ValueError:
        return default


def _env_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    # Where Ollama is listening. Matches Ollama's own OLLAMA_HOST convention.
    ollama_host: str = "http://localhost:11434"
    # Chat model used for study packs, quizzes, grading and flashcards.
    chat_model: str = "llama3.2:3b"
    # Embedding model used for semantic search. Optional: if it is not pulled,
    # retrieval falls back to keyword (BM25) search.
    embed_model: str = "nomic-embed-text"
    # Context window requested from Ollama. 8k fits comfortably on 8 GB RAM
    # with a 3B model.
    num_ctx: int = 8192
    # Seconds to wait for a single generation. Small CPUs can be slow.
    request_timeout: int = 300
    # Whisper model size for lecture recordings (tiny/base/small/medium).
    whisper_model: str = "base"
    # Root folder for the SQLite database and uploaded files. Deliberately
    # outside the repo so personal notes can never be committed by accident.
    data_dir: Path = field(default_factory=lambda: Path.home() / ".kuki")
    # Largest upload accepted, in megabytes.
    max_upload_mb: int = 200
    # Allow the open-course importer to reach the internet.
    allow_downloads: bool = True
    # Built web app to serve at "/" (frontend/dist). None disables it.
    web_dir: Path | None = field(default_factory=lambda: Path(__file__).resolve().parents[2] / "frontend" / "dist")

    @property
    def db_path(self) -> Path:
        return self.data_dir / "kuki.db"

    @property
    def uploads_dir(self) -> Path:
        return self.data_dir / "uploads"

    def ensure_dirs(self) -> None:
        """Create the data folders on first run."""
        self.uploads_dir.mkdir(parents=True, exist_ok=True)


def load_settings() -> Settings:
    """Build settings from the current environment (uncached, for tests)."""
    defaults = Settings()
    return Settings(
        ollama_host=os.getenv("OLLAMA_HOST", defaults.ollama_host).rstrip("/"),
        chat_model=os.getenv("KUKI_MODEL", defaults.chat_model),
        embed_model=os.getenv("KUKI_EMBED_MODEL", defaults.embed_model),
        num_ctx=_env_int("KUKI_NUM_CTX", defaults.num_ctx, minimum=2048),
        request_timeout=_env_int("KUKI_TIMEOUT", defaults.request_timeout),
        whisper_model=os.getenv("KUKI_WHISPER_MODEL", defaults.whisper_model),
        data_dir=Path(os.getenv("KUKI_DATA_DIR", str(defaults.data_dir))).expanduser(),
        max_upload_mb=_env_int("KUKI_MAX_UPLOAD_MB", defaults.max_upload_mb),
        allow_downloads=_env_bool("KUKI_ALLOW_DOWNLOADS", defaults.allow_downloads),
        web_dir=Path(os.environ["KUKI_WEB_DIR"]) if os.getenv("KUKI_WEB_DIR") else defaults.web_dir,
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Process-wide settings, read once."""
    return load_settings()
