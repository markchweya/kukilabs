from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv(".env.local")

@dataclass(frozen=True)
class Settings:
    admin_password: str
    data_dir: Path
    uploads_dir: Path
    index_dir: Path
    llm_model_path: Path
    embed_model_name: str

def get_settings() -> Settings:
    data_dir = Path(os.getenv("DATA_DIR", ".\\data")).resolve()
    uploads_dir = data_dir / "uploads"
    index_dir = data_dir / "index"
    uploads_dir.mkdir(parents=True, exist_ok=True)
    index_dir.mkdir(parents=True, exist_ok=True)

    return Settings(
        admin_password=os.getenv("ADMIN_PASSWORD", "change-me-now"),
        data_dir=data_dir,
        uploads_dir=uploads_dir,
        index_dir=index_dir,
        llm_model_path=Path(os.getenv("LLM_MODEL_PATH", ".\\models\\llm\\model.gguf")).resolve(),
        embed_model_name=os.getenv("EMBED_MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2"),
    )
