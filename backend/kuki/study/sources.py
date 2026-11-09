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

from kuki.search.bm25 import tokenize
from kuki.search.hybrid import Passage

# An extra citation must share at least this fraction of the claim's content
# words with its passage, and at least half as much as the best citation.
MIN_SUPPORT = 0.25


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

    def resolve(self, tags: list[str], claim: str | None = None) -> list[Citation]:
        """Map model-cited tags to citations, dropping unknown and duplicate tags.

        With `claim`, extra citations that barely relate to it are dropped too.
        A real Llama 3.2 3B run cited the same generic slide on almost every
        item; the best-matching citation is always kept.
        """
        seen: set[str] = set()
        valid: list[str] = []
        for raw in tags:
            tag = raw.strip().strip("[]").upper()
            if tag in seen or tag not in self.by_tag:
                continue
            seen.add(tag)
            valid.append(tag)
        if claim and len(valid) > 1:
            valid = self._prune(valid, claim)
        out: list[Citation] = []
        for tag in valid:
            p = self.by_tag[tag]
            out.append(Citation(
                segment_id=p.segment_id,
                document_id=p.document_id,
                document_title=p.document_title,
                locator=p.locator,
                excerpt=_excerpt(p.text),
            ))
        return out

    def _prune(self, tags: list[str], claim: str) -> list[str]:
        terms = content_stems(claim)
        if not terms:
            return tags
        support = {t: len(terms & content_stems(self.by_tag[t].text)) / len(terms) for t in tags}
        best = max(support.values())
        return [t for t in tags if support[t] == best or (support[t] >= MIN_SUPPORT and support[t] >= best / 2)]


def content_stems(text: str) -> set[str]:
    """Content words, lightly stemmed so 'costs'/'cost' and 'uses'/'using'/'use' match."""
    return {_stem(w) for w in tokenize(text)}


def _stem(word: str) -> str:
    if len(word) > 4 and word.endswith("ing"):
        word = word[:-3]
    elif len(word) > 3 and word.endswith("s") and not word.endswith("ss"):
        word = word[:-1]
    if len(word) > 2 and word.endswith("e"):
        word = word[:-1]
    return word


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
