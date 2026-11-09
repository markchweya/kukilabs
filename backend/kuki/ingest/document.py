"""Word reader: one segment per heading-delimited section.

Word documents have no pages we can reliably address, so we use the nearest
heading as the locator ("Section: Binary Search"), which is what a student
would scroll to anyway.
"""

from __future__ import annotations

from pathlib import Path

import docx
from docx.opc.exceptions import PackageNotFoundError

from kuki.ingest.base import ExtractionError, Segment, clean_text


def read_docx(path: Path) -> list[Segment]:
    try:
        document = docx.Document(str(path))
    except (PackageNotFoundError, KeyError, ValueError) as exc:
        raise ExtractionError("Could not open this Word document.") from exc

    segments: list[Segment] = []
    heading = "Introduction"
    buffer: list[str] = []

    def flush() -> None:
        text = clean_text("\n".join(buffer))
        if text:
            segments.append(Segment(f"Section: {heading}", text))
        buffer.clear()

    for para in document.paragraphs:
        style = (para.style.name if para.style is not None else "") or ""
        if style.lower().startswith(("heading", "title")) and para.text.strip():
            flush()
            heading = para.text.strip()[:80]
        elif para.text.strip():
            buffer.append(para.text)
    flush()

    # Tables are appended as their own section so their content is searchable.
    for number, table in enumerate(document.tables, start=1):
        rows = [" | ".join(c.text.strip() for c in row.cells) for row in table.rows]
        text = clean_text("\n".join(r for r in rows if r.strip(" |")))
        if text:
            segments.append(Segment(f"Table {number}", text))
    return segments
