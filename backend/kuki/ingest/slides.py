"""PowerPoint reader: one segment per slide, including speaker notes.

Lecturers often put the real explanation in the speaker notes and only
keywords on the slide, so notes are included and labelled as such.
"""

from __future__ import annotations

from pathlib import Path

from pptx import Presentation
from pptx.exc import PackageNotFoundError

from kuki.ingest.base import ExtractionError, Segment, clean_text


def _shape_text(shape) -> list[str]:
    """Collect text from a shape, recursing into groups and tables."""
    out: list[str] = []
    if getattr(shape, "shape_type", None) == 6:  # MSO_SHAPE_TYPE.GROUP
        for child in shape.shapes:
            out.extend(_shape_text(child))
    if getattr(shape, "has_text_frame", False) and shape.text_frame.text.strip():
        out.append(shape.text_frame.text)
    if getattr(shape, "has_table", False):
        for row in shape.table.rows:
            cells = [c.text.strip() for c in row.cells]
            if any(cells):
                out.append(" | ".join(cells))
    return out


def read_slides(path: Path) -> list[Segment]:
    try:
        deck = Presentation(str(path))
    except (PackageNotFoundError, KeyError, ValueError) as exc:
        raise ExtractionError("Could not open this PowerPoint file.") from exc

    segments: list[Segment] = []
    for number, slide in enumerate(deck.slides, start=1):
        parts: list[str] = []
        for shape in slide.shapes:
            parts.extend(_shape_text(shape))
        if slide.has_notes_slide:
            notes = slide.notes_slide.notes_text_frame.text.strip()
            if notes:
                parts.append(f"Speaker notes: {notes}")
        text = clean_text("\n".join(parts))
        if text:
            segments.append(Segment(f"Slide {number}", text))
    return segments
