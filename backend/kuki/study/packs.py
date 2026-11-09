"""Study pack generation.

Long documents do not fit in a small model's context, so we work map-style:
each batch of passages produces a partial pack with its own citations, and the
parts are merged in code (never by the model), so no citation can be lost or
rewritten during merging. One last short call writes the title and overview.
"""

from __future__ import annotations

import json
import logging
from typing import Literal

from kuki.config import Settings
from kuki.db import transaction
from kuki.library import Library, NotFound
from kuki.llm import OllamaClient, OllamaError
from kuki.search.hybrid import Passage
from kuki.study import prompts
from kuki.study.extractive import extractive_concepts, extractive_examples, extractive_points
from kuki.study.pack_models import (
    Concept,
    Example,
    KeyPoint,
    Mistake,
    PackSummaryDraft,
    StudyPack,
    StudyPackDraft,
)
from kuki.study.sources import SourceSet, batch_by_size

log = logging.getLogger(__name__)

Knowledge = Literal["notes_only", "fill_gaps"]

# Rough characters-per-token for English lecture text.
CHARS_PER_TOKEN = 3.5
# Tokens held back for the instructions and the model's answer.
RESERVED_TOKENS = 2500
MAX_ITEMS = {"concepts": 12, "key_points": 12, "examples": 5, "common_mistakes": 6}


def source_budget(settings: Settings) -> int:
    """How many characters of source text fit in one prompt."""
    return int(max(2000, (settings.num_ctx - RESERVED_TOKENS) * CHARS_PER_TOKEN))


def generate_pack(
    library: Library, llm: OllamaClient, doc_id: str, knowledge: Knowledge = "notes_only"
) -> StudyPack:
    doc = library.get_document(doc_id)
    passages = library.passages([doc_id])
    if not passages:
        raise NotFound("This document has no readable text yet.")

    try:
        pack = _ai_pack(library.settings, llm, doc.id, doc.title, passages, knowledge)
    except OllamaError as exc:
        log.info("AI pack failed (%s); building extractive pack instead.", exc)
        pack = extractive_pack(doc.id, doc.title, passages, knowledge)
        pack.notice = f"Kuki's AI is offline, so this pack was copied straight from your notes. ({exc})"

    save_pack(library, pack)
    return pack


def _ai_pack(
    settings: Settings,
    llm: OllamaClient,
    doc_id: str,
    title_hint: str,
    passages: list[Passage],
    knowledge: Knowledge,
) -> StudyPack:
    concepts: list[Concept] = []
    points: list[KeyPoint] = []
    examples: list[Example] = []
    mistakes: list[Mistake] = []

    tag_offset = 1
    for batch in batch_by_size(passages, source_budget(settings)):
        # Offsetting the numbering keeps tags unique across batches, which
        # makes logs and debugging much less confusing.
        sources = SourceSet.number(batch, start=tag_offset)
        tag_offset += len(batch)
        draft = llm.chat_json(
            settings.chat_model,
            [
                {"role": "system", "content": prompts.TUTOR},
                {"role": "user", "content": prompts.study_pack(sources.render(), knowledge)},
            ],
            StudyPackDraft,
            num_ctx=settings.num_ctx,
        )
        concepts += [Concept(term=c.term, explanation=c.explanation, citations=sources.resolve(c.sources)) for c in draft.concepts]
        points += [KeyPoint(point=p.point, citations=sources.resolve(p.sources)) for p in draft.key_points]
        examples += [Example(title=e.title, explanation=e.explanation, citations=sources.resolve(e.sources)) for e in draft.examples]
        mistakes += [Mistake(mistake=m.mistake, correction=m.correction, citations=sources.resolve(m.sources)) for m in draft.common_mistakes]

    if knowledge == "notes_only":
        # In notes-only mode an item with no valid citation is most likely a
        # hallucination, so it is removed rather than shown with a warning.
        concepts, points, examples, mistakes = (
            [i for i in items if i.grounded] for items in (concepts, points, examples, mistakes)
        )

    concepts = _dedupe(concepts, key=lambda c: c.term.lower().strip())
    points = _dedupe(points, key=lambda p: p.point.lower().strip())

    title, overview = _summarise(settings, llm, title_hint, [p.point for p in points])
    return StudyPack(
        document_id=doc_id,
        title=title,
        overview=overview,
        mode="ai",
        model=settings.chat_model,
        knowledge=knowledge,
        concepts=concepts[: MAX_ITEMS["concepts"]],
        key_points=points[: MAX_ITEMS["key_points"]],
        examples=examples[: MAX_ITEMS["examples"]],
        common_mistakes=mistakes[: MAX_ITEMS["common_mistakes"]],
    )


def _summarise(settings: Settings, llm: OllamaClient, hint: str, points: list[str]) -> tuple[str, str]:
    """Title and overview. A failure here should not throw away a whole pack."""
    if not points:
        return hint, ""
    try:
        summary = llm.chat_json(
            settings.chat_model,
            [{"role": "system", "content": prompts.TUTOR}, {"role": "user", "content": prompts.pack_summary(points, hint)}],
            PackSummaryDraft,
            num_ctx=settings.num_ctx,
        )
        return summary.title.strip() or hint, summary.overview.strip()
    except OllamaError as exc:
        log.info("Summary failed (%s); using document title.", exc)
        return hint, " ".join(points[:2])


def _dedupe(items: list, key) -> list:
    seen: set = set()
    out = []
    for item in items:
        k = key(item)
        if k and k not in seen:
            seen.add(k)
            out.append(item)
    return out


def extractive_pack(doc_id: str, title: str, passages: list[Passage], knowledge: Knowledge) -> StudyPack:
    points = extractive_points(passages)
    return StudyPack(
        document_id=doc_id,
        title=title,
        overview=" ".join(p.point for p in points[:2]),
        mode="extractive",
        model=None,
        knowledge=knowledge,
        concepts=extractive_concepts(passages),
        key_points=points,
        examples=extractive_examples(passages),
        common_mistakes=[],
    )


# ---- persistence ----------------------------------------------------------


def save_pack(library: Library, pack: StudyPack) -> None:
    with transaction(library.conn):
        library.conn.execute(
            "INSERT INTO study_packs(document_id, payload) VALUES (?, ?)"
            " ON CONFLICT(document_id) DO UPDATE SET payload = excluded.payload, created_at = datetime('now')",
            (pack.document_id, pack.model_dump_json()),
        )


def load_pack(library: Library, doc_id: str) -> StudyPack | None:
    row = library.conn.execute("SELECT payload FROM study_packs WHERE document_id = ?", (doc_id,)).fetchone()
    return StudyPack.model_validate(json.loads(row[0])) if row else None
