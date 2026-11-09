"""A study pack built without any language model.

This is the backup path for when Ollama is not running. It is plainer than the
AI pack but it is never wrong about the source: every line is copied from the
student's own material and cited to where it came from.
"""

from __future__ import annotations

import re

from kuki.search.hybrid import Passage
from kuki.study.pack_models import Concept, Example, KeyPoint
from kuki.study.sources import SourceSet

# "Term: definition" on its own line, as lecture slides love to do.
_COLON_DEF = re.compile(r"^\s*[-•*]?\s*([A-Z][\w\s()\-/*+]{1,40}?)\s*[:–—]\s+(.{12,240})$", re.M)
# "A heap is a tree-based structure ..." style sentences.
_IS_DEF = re.compile(r"^((?:An?|The)\s+)?([A-Z]?[\w\-*+ ]{2,40}?)\s+(?:is|are|refers to|means)\s+(an?\s|the\s)?(.{12,200}?)[.!]", re.I)
_SENTENCE = re.compile(r"(?<=[.!?])\s+")


def sentences(text: str) -> list[str]:
    flat = " ".join(text.split())
    return [s.strip() for s in _SENTENCE.split(flat) if len(s.strip()) > 20]


def extractive_concepts(passages: list[Passage], limit: int = 8) -> list[Concept]:
    sources = SourceSet.number(passages)
    found: dict[str, Concept] = {}
    for tag, p in sources.by_tag.items():
        candidates = [(m.group(1), m.group(2)) for m in _COLON_DEF.finditer(p.text)]
        for s in sentences(p.text):
            m = _IS_DEF.match(s)
            if m:
                candidates.append((m.group(2), s))
        for term, explanation in candidates:
            key = term.strip().lower()
            if key and key not in found and len(found) < limit:
                found[key] = Concept(term=term.strip(), explanation=explanation.strip(), citations=sources.resolve([tag]))
    return list(found.values())


def extractive_points(passages: list[Passage], limit: int = 8) -> list[KeyPoint]:
    """The first substantial sentence of each passage, spread across the document."""
    sources = SourceSet.number(passages)
    tags = list(sources.by_tag)
    step = max(1, len(tags) // limit)
    points = []
    for tag in tags[::step][:limit]:
        first = next(iter(sentences(sources.by_tag[tag].text)), None)
        if first:
            points.append(KeyPoint(point=first, citations=sources.resolve([tag])))
    return points


def extractive_examples(passages: list[Passage], limit: int = 3) -> list[Example]:
    sources = SourceSet.number(passages)
    out = []
    for tag, p in sources.by_tag.items():
        for s in sentences(p.text):
            if re.search(r"\b(for example|e\.g\.|for instance|example:)", s, re.I):
                out.append(Example(title=f"From {p.locator}", explanation=s, citations=sources.resolve([tag])))
                break
        if len(out) >= limit:
            break
    return out
