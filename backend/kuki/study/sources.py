"""Numbered source blocks and citation checking.

The model never sees bare text. Every passage is shown with a short tag
("S3") and its location, and the model must cite tags for every claim. After
generation we resolve tags back to real segments and drop any tag the model
invented. Claims left with no valid source are shown to the student as "not
found in your notes" rather than silently trusted.
"""

from __future__ import annotations

from dataclasses import dataclass

from pydantic import BaseModel

from kuki.search.hybrid import Passage


class Citation(BaseModel):
    """A checkable pointer back into the student's material."""

    segment_id: int
    document_id: str
    document_title: str
    locator: str
    excerpt: str


@dataclass
class SourceSet:
    """Passages keyed by the tag the model sees."""

    by_tag: dict[str, Passage]

    @classmethod
    def number(cls, passages: list[Passage], start: int = 1) -> "SourceSet":
        return cls({f"S{i}": p for i, p in enumerate(passages, start=start)})

    def render(self, max_chars_each: int = 1800) -> str:
        """Format sources for a prompt."""
        blocks = []
        for tag, p in self.by_tag.items():
            text = p.text if len(p.text) <= max_chars_each else p.text[:max_chars_each] + " …"
            blocks.append(f"[{tag}] ({p.document_title}, {p.locator})\n{text}")
        return "\n\n".join(blocks)

    def resolve(self, tags: list[str]) -> list[Citation]:
        """Map model-cited tags to citations, dropping unknown and duplicate tags."""
        seen: set[str] = set()
        out: list[Citation] = []
        for raw in tags:
            tag = raw.strip().strip("[]").upper()
            if tag in seen or tag not in self.by_tag:
                continue
            seen.add(tag)
            p = self.by_tag[tag]
            out.append(Citation(
                segment_id=p.segment_id,
                document_id=p.document_id,
                document_title=p.document_title,
                locator=p.locator,
                excerpt=_excerpt(p.text),
            ))
        return out


def _excerpt(text: str, limit: int = 240) -> str:
    text = " ".join(text.split())
    return text if len(text) <= limit else text[: limit - 1].rsplit(" ", 1)[0] + "…"


def batch_by_size(passages: list[Passage], max_chars: int) -> list[list[Passage]]:
    """Group passages in reading order into batches that fit the context budget."""
    batches: list[list[Passage]] = []
    current: list[Passage] = []
    size = 0
    for p in passages:
        if current and size + len(p.text) > max_chars:
            batches.append(current)
            current, size = [], 0
        current.append(p)
        size += len(p.text)
    if current:
        batches.append(current)
    return batches
