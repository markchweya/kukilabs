"""PDF reader: one segment per page."""

from __future__ import annotations

from pathlib import Path

from pypdf import PdfReader
from pypdf.errors import PdfReadError

from kuki.ingest.base import ExtractionError, Segment, clean_text


def read_pdf(path: Path) -> list[Segment]:
    try:
        reader = PdfReader(str(path))
        if reader.is_encrypted:
            # Many lecture PDFs are "encrypted" with an empty password just to
            # block editing; try that before giving up.
            if not reader.decrypt(""):
                raise ExtractionError("This PDF is password-protected.")
    except PdfReadError as exc:
        raise ExtractionError(f"Could not open PDF: {exc}") from exc

    segments: list[Segment] = []
    for number, page in enumerate(reader.pages, start=1):
        text = clean_text(page.extract_text() or "")
        if text:
            segments.append(Segment(f"Page {number}", text))
    return segments
