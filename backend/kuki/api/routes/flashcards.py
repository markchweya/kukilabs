"""Flashcard endpoints: generate, review queue, grading, stats."""

from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, Depends, Response
from pydantic import BaseModel, Field

from kuki.api.deps import ensure_ready, get_library, get_llm
from kuki.library import Library
from kuki.llm import OllamaClient
from kuki.study import flashcards as fc

router = APIRouter(tags=["flashcards"])


class CardsRequest(BaseModel):
    count: int = Field(12, ge=1, le=30)


class ReviewRequest(BaseModel):
    button: Literal["again", "hard", "good", "easy"]


@router.post("/api/documents/{doc_id}/flashcards", response_model=list[fc.Flashcard])
def create_cards(
    doc_id: str,
    body: CardsRequest | None = None,
    library: Library = Depends(get_library),
    llm: OllamaClient = Depends(get_llm),
) -> list[fc.Flashcard]:
    ensure_ready(library, doc_id)
    return fc.generate_cards(library, llm, doc_id, (body or CardsRequest()).count)


@router.get("/api/documents/{doc_id}/flashcards", response_model=list[fc.Flashcard])
def list_cards(doc_id: str, library: Library = Depends(get_library)) -> list[fc.Flashcard]:
    library.get_document(doc_id)
    return fc.all_cards(library, doc_id)


@router.get("/api/flashcards/due", response_model=list[fc.Flashcard])
def due(document_id: str | None = None, limit: int = 20, library: Library = Depends(get_library)) -> list[fc.Flashcard]:
    return fc.due_cards(library, document_id, max(1, min(limit, 100)))


@router.get("/api/flashcards/stats", response_model=fc.DeckStats)
def stats(document_id: str | None = None, library: Library = Depends(get_library)) -> fc.DeckStats:
    return fc.deck_stats(library, document_id)


@router.post("/api/flashcards/{card_id}/review", response_model=fc.Flashcard)
def review(card_id: int, body: ReviewRequest, library: Library = Depends(get_library)) -> fc.Flashcard:
    return fc.review_card(library, card_id, body.button)


@router.delete("/api/flashcards/{card_id}", status_code=204)
def delete(card_id: int, library: Library = Depends(get_library)) -> None:
    fc.delete_card(library, card_id)


@router.get("/api/documents/{doc_id}/flashcards/anki.txt")
def export_anki(doc_id: str, library: Library = Depends(get_library)) -> Response:
    """Export the deck as an Anki-importable text file (File > Import in Anki).

    Uses Anki's file headers so the separator and tags column are detected
    automatically. Each back side keeps its source so cards stay checkable.
    """
    doc = library.get_document(doc_id)
    tag = "kuki::" + "".join(ch if ch.isalnum() else "_" for ch in doc.title)[:60]
    lines = ["#separator:tab", "#html:false", "#tags column:3"]
    for card in fc.all_cards(library, doc_id):
        sources = ", ".join(c.locator for c in card.citations)
        back = f"{card.back} (Source: {doc.title}, {sources})" if sources else card.back
        lines.append("\t".join(_clean(x) for x in (card.front, back, tag)))
    return Response(
        "\n".join(lines) + "\n",
        media_type="text/plain; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="kuki-{doc_id}-anki.txt"'},
    )


def _clean(field: str) -> str:
    """Tabs and newlines would break Anki's row/column parsing."""
    return " ".join(field.replace("\t", " ").split())
