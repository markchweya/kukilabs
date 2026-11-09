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
