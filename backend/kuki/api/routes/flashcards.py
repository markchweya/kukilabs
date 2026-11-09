"""Flashcard endpoints: generate, review queue, grading, stats."""

from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, Depends
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
