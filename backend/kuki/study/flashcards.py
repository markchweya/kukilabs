"""Flashcard generation and spaced-repetition reviews."""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone

from pydantic import BaseModel, Field

from kuki.db import transaction
from kuki.library import Library, NotFound
from kuki.llm import OllamaClient, OllamaError
from kuki.study import prompts
from kuki.study.extractive import extractive_concepts
from kuki.study.packs import source_budget
from kuki.study.quiz import spread_sample
from kuki.study.sources import Citation, SourceSet
from kuki.study.srs import BUTTONS, CardState, next_due, review

log = logging.getLogger(__name__)

# SQLite's datetime('now') format, so Python- and SQL-written dates compare correctly.
SQL_TIME = "%Y-%m-%d %H:%M:%S"


class CardDraft(BaseModel):
    front: str
    back: str
    sources: list[str]


class DeckDraft(BaseModel):
    cards: list[CardDraft]


class Flashcard(BaseModel):
    id: int
    document_id: str
    front: str
    back: str
    citations: list[Citation]
    due_at: str
    interval_days: int
    repetitions: int
    lapses: int


class DeckStats(BaseModel):
    total: int
    due_now: int
    learned: int  # reviewed successfully at least once


def _now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def generate_cards(library: Library, llm: OllamaClient, doc_id: str, count: int = 12) -> list[Flashcard]:
    library.get_document(doc_id)
    passages = library.passages([doc_id])
    if not passages:
        raise NotFound("This document has no readable text yet.")
    count = max(1, min(count, 30))

    sources = SourceSet.number(spread_sample(passages, source_budget(library.settings)))
    try:
        deck = llm.chat_json(
            library.settings.chat_model,
            [
                {"role": "system", "content": prompts.TUTOR},
                {"role": "user", "content": prompts.flashcards(sources.render(), count)},
            ],
            DeckDraft,
            num_ctx=library.settings.num_ctx,
        )
        cards = [(c.front, c.back, sources.resolve(c.sources)) for c in deck.cards[:count]]
        cards = [c for c in cards if c[2] and c[0].strip() and c[1].strip()]
    except OllamaError as exc:
        log.info("AI flashcards failed (%s); using extracted definitions.", exc)
        cards = [(c.term, c.explanation, c.citations) for c in extractive_concepts(passages, limit=count)]

    # Skip cards whose front already exists in this deck (regenerating should add, not duplicate).
    existing = {
        r[0].strip().lower()
        for r in library.conn.execute("SELECT front FROM flashcards WHERE document_id = ?", (doc_id,))
    }
    created = []
    with transaction(library.conn):
        for front, back, cites in cards:
            if front.strip().lower() in existing:
                continue
            existing.add(front.strip().lower())
            cur = library.conn.execute(
                "INSERT INTO flashcards(document_id, front, back, citations) VALUES (?, ?, ?, ?)",
                (doc_id, front.strip(), back.strip(), json.dumps([c.model_dump() for c in cites])),
            )
            created.append(cur.lastrowid)
    return [get_card(library, cid) for cid in created]
