"""Plain text and Markdown reader.

Markdown headings become locators; plain text is grouped into blocks of
paragraphs labelled by paragraph number.
"""

from __future__ import annotations

import re
from pathlib import Path

from kuki.ingest.base import Segment, clean_text

_HEADING = re.compile(r"^#{1,6}\s+(.+)$")


def read_text(path: Path) -> list[Segment]:
    raw = path.read_bytes()
    # Lecture notes come from many editors; utf-8-sig drops a BOM, and latin-1
    # is a last resort that can decode any byte sequence.
    for encoding in ("utf-8-sig", "utf-16", "latin-1"):
        try:
            text = raw.decode(encoding)
            break
        except UnicodeDecodeError:
            continue
    return segment_text(text)


def segment_text(text: str, paragraphs_per_segment: int = 4) -> list[Segment]:
    """Segment raw text. Shared with the web importer."""
    lines = clean_text(text).split("\n")
    if any(_HEADING.match(l) for l in lines):
        return _by_heading(lines)

    paragraphs = [p.strip() for p in "\n".join(lines).split("\n\n") if p.strip()]
    segments = []
    for start in range(0, len(paragraphs), paragraphs_per_segment):
        chunk = paragraphs[start : start + paragraphs_per_segment]
        label = f"Paragraphs {start + 1}-{start + len(chunk)}" if len(chunk) > 1 else f"Paragraph {start + 1}"
        segments.append(Segment(label, "\n\n".join(chunk)))
    return segments


def _by_heading(lines: list[str]) -> list[Segment]:
    segments: list[Segment] = []
    heading, buffer = "Introduction", []
    for line in lines:
        match = _HEADING.match(line)
        if match:
            if "".join(buffer).strip():
                segments.append(Segment(f"Section: {heading}", clean_text("\n".join(buffer))))
            heading, buffer = match.group(1).strip()[:80], []
        else:
            buffer.append(line)
    if "".join(buffer).strip():
        segments.append(Segment(f"Section: {heading}", clean_text("\n".join(buffer))))
    return segments
