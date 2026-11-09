"""Shared types for document readers.

Every reader turns a file into a list of `Segment`s: a chunk of text plus a
human-readable `locator` saying where it came from ("Slide 4", "Page 12",
"12:30"). Locators are what make Kuki's citations checkable by a student.
"""

from __future__ import annotations

import re
from dataclasses import dataclass


class ExtractionError(RuntimeError):
    """The file could not be read (corrupt, encrypted, unsupported...)."""


class MissingDependency(ExtractionError):
    """An optional extra (OCR, Whisper) is needed but not installed."""


@dataclass(frozen=True)
class Segment:
    locator: str
    text: str


def clean_text(text: str) -> str:
    """Normalise whitespace while keeping paragraph breaks."""
    text = text.replace("\r\n", "\n").replace("\r", "\n").replace(" ", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r" *\n *", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def split_long(segment: Segment, max_chars: int = 1500, overlap: int = 150) -> list[Segment]:
    """Split an oversized segment into pieces that fit a retrieval chunk.

    A dense PDF page can hold far more text than is useful in one search hit.
    We break on paragraph, then sentence, boundaries where possible, keep a
    small overlap so ideas spanning a cut are still findable, and suffix the
    locator ("Page 3 (2/3)") so citations stay precise.
    """
    text = segment.text
    if len(text) <= max_chars:
        return [segment]

    pieces: list[str] = []
    start = 0
    while start < len(text):
        end = min(len(text), start + max_chars)
        if end < len(text):
            # Prefer to cut at a paragraph break, then a sentence end, then a space.
            window = text[start:end]
            for sep in ("\n\n", ". ", "\n", " "):
                cut = window.rfind(sep)
                if cut > max_chars // 2:
                    end = start + cut + len(sep)
                    break
        pieces.append(text[start:end].strip())
        if end >= len(text):
            break
        start = max(end - overlap, start + 1)

    total = len(pieces)
    return [Segment(f"{segment.locator} ({i}/{total})", p) for i, p in enumerate(pieces, start=1) if p]
