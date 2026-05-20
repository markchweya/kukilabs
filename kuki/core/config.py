from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os

from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parents[2]

load_dotenv(REPO_ROOT / ".env.local")


def _int_env(name: str, default: int, *, minimum: int = 1) -> int:
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        return max(minimum, int(raw))
    except (TypeError, ValueError):
        return default


@dataclass(frozen=True)
class Settings:
    admin_password: str
    data_dir: Path
    uploads_dir: Path
    index_dir: Path
    llm_model_path: Path
    llm_n_ctx: int
    llm_n_threads: int
    llm_max_tokens: int
    embed_model_name: str


def get_settings() -> Settings:
    data_dir = Path(os.getenv("DATA_DIR", str(REPO_ROOT / "data"))).resolve()
    uploads_dir = data_dir / "uploads"
    index_dir = data_dir / "index"
    uploads_dir.mkdir(parents=True, exist_ok=True)
    index_dir.mkdir(parents=True, exist_ok=True)

    default_threads = max(1, (os.cpu_count() or 2) - 1)
    default_model_path = REPO_ROOT / "models" / "llm" / "model.gguf"
    if os.getenv("LLM_MODEL_PATH"):
        llm_model_path = Path(os.getenv("LLM_MODEL_PATH", "")).resolve()
    else:
        model_candidates = sorted((REPO_ROOT / "models" / "llm").glob("*.gguf"))
        llm_model_path = (model_candidates[0] if model_candidates else default_model_path).resolve()

    return Settings(
        admin_password=os.getenv("ADMIN_PASSWORD", "change-me-now"),
        data_dir=data_dir,
        uploads_dir=uploads_dir,
        index_dir=index_dir,
        llm_model_path=llm_model_path,
        llm_n_ctx=_int_env("LLM_N_CTX", 4096),
        llm_n_threads=_int_env("LLM_N_THREADS", default_threads),
        llm_max_tokens=_int_env("LLM_MAX_TOKENS", 900),
        embed_model_name=os.getenv("EMBED_MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2"),
    )
