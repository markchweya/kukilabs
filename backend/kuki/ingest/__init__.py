"""Turn any supported file into located text segments.

`extract()` picks a reader from the file extension, then splits oversized
segments so every piece is a good size for search and for the model's context.
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from kuki.ingest.audio import read_audio
from kuki.ingest.base import ExtractionError, MissingDependency, Segment, split_long
from kuki.ingest.document import read_docx
from kuki.ingest.image import read_image
from kuki.ingest.pdf import read_pdf
from kuki.ingest.plaintext import read_text
from kuki.ingest.slides import read_slides

# extension -> (document kind, reader)
READERS: dict[str, tuple[str, Callable[[Path], list[Segment]]]] = {
    ".pdf": ("pdf", read_pdf),
    ".pptx": ("slides", read_slides),
    ".docx": ("doc", read_docx),
    ".txt": ("text", read_text),
    ".md": ("text", read_text),
    ".markdown": ("text", read_text),
    ".png": ("image", read_image),
    ".jpg": ("image", read_image),
    ".jpeg": ("image", read_image),
    ".webp": ("image", read_image),
    ".bmp": ("image", read_image),
    ".mp3": ("audio", read_audio),
    ".m4a": ("audio", read_audio),
    ".wav": ("audio", read_audio),
    ".ogg": ("audio", read_audio),
    ".webm": ("audio", read_audio),
    ".mp4": ("audio", read_audio),  # video lectures: we only need the soundtrack
}

SUPPORTED_EXTENSIONS = sorted(READERS)


def kind_for(filename: str) -> str:
    """Document kind for a filename, or raise if unsupported."""
    ext = Path(filename).suffix.lower()
    if ext not in READERS:
        raise ExtractionError(
            f"Kuki can't read '{ext or filename}' files yet. Supported: {', '.join(SUPPORTED_EXTENSIONS)}"
        )
    return READERS[ext][0]


def extract(path: Path) -> list[Segment]:
    kind_for(path.name)  # validates the extension
    _kind, reader = READERS[path.suffix.lower()]
    segments = reader(path)
    if not segments:
        raise ExtractionError("No readable text was found in this file.")
    return [piece for seg in segments for piece in split_long(seg)]


__all__ = ["ExtractionError", "MissingDependency", "Segment", "SUPPORTED_EXTENSIONS", "extract", "kind_for"]
