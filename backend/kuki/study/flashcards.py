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
from kuki.study.text import clean
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
    ease: float
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
        cards = [(clean(c.front), clean(c.back), sources.resolve(c.sources, f"{c.front} {c.back}")) for c in deck.cards[:count]]
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


# ---- reading and reviewing -------------------------------------------------

_CARD_COLUMNS = "id, document_id, front, back, citations, due_at, ease, interval_days, repetitions, lapses"


def _to_card(row) -> Flashcard:
    data = dict(row)
    data["citations"] = json.loads(data["citations"])
    return Flashcard(**data)


def get_card(library: Library, card_id: int) -> Flashcard:
    row = library.conn.execute(f"SELECT {_CARD_COLUMNS} FROM flashcards WHERE id = ?", (card_id,)).fetchone()
    if row is None:
        raise NotFound(f"No flashcard with id {card_id}")
    return _to_card(row)


def due_cards(library: Library, document_id: str | None = None, limit: int = 20) -> list[Flashcard]:
    """Cards due now, most overdue first. New cards count as due."""
    sql = f"SELECT {_CARD_COLUMNS} FROM flashcards WHERE due_at <= ?"
    params: list = [_now().strftime(SQL_TIME)]
    if document_id:
        sql += " AND document_id = ?"
        params.append(document_id)
    sql += " ORDER BY due_at, id LIMIT ?"
    params.append(limit)
    return [_to_card(r) for r in library.conn.execute(sql, params)]


def all_cards(library: Library, document_id: str) -> list[Flashcard]:
    rows = library.conn.execute(
        f"SELECT {_CARD_COLUMNS} FROM flashcards WHERE document_id = ? ORDER BY id", (document_id,)
    )
    return [_to_card(r) for r in rows]


def review_card(library: Library, card_id: int, button: str) -> Flashcard:
    """Apply an Again/Hard/Good/Easy review and reschedule the card."""
    if button not in BUTTONS:
        raise ValueError(f"button must be one of {', '.join(BUTTONS)}")
    row = library.conn.execute(
        "SELECT ease, interval_days, repetitions, lapses FROM flashcards WHERE id = ?", (card_id,)
    ).fetchone()
    if row is None:
        raise NotFound(f"No flashcard with id {card_id}")

    state = review(CardState(*row), BUTTONS[button])
    due = next_due(state, _now()).strftime(SQL_TIME)
    with transaction(library.conn):
        library.conn.execute(
            "UPDATE flashcards SET ease = ?, interval_days = ?, repetitions = ?, lapses = ?, due_at = ? WHERE id = ?",
            (state.ease, state.interval_days, state.repetitions, state.lapses, due, card_id),
        )
        library.conn.execute("INSERT INTO reviews(card_id, grade) VALUES (?, ?)", (card_id, BUTTONS[button]))
    return get_card(library, card_id)


def deck_stats(library: Library, document_id: str | None = None) -> DeckStats:
    where, params = ("WHERE document_id = ?", [document_id]) if document_id else ("", [])
    total, learned = library.conn.execute(
        f"SELECT COUNT(*), COALESCE(SUM(repetitions > 0), 0) FROM flashcards {where}", params
    ).fetchone()
    return DeckStats(total=total, due_now=len(due_cards(library, document_id, limit=10_000)), learned=learned)


def delete_card(library: Library, card_id: int) -> None:
    get_card(library, card_id)
    with transaction(library.conn):
        library.conn.execute("DELETE FROM flashcards WHERE id = ?", (card_id,))
