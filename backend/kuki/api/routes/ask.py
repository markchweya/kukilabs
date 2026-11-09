"""Ask Kuki and raw search endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from kuki.api.deps import get_library, get_llm
from kuki.library import Library
from kuki.llm import OllamaClient
from kuki.study.ask import Answer, ask

router = APIRouter(tags=["ask"])


class AskRequest(BaseModel):
    question: str = Field(min_length=1, max_length=1000)
    document_ids: list[str] | None = None


class SearchHit(BaseModel):
    segment_id: int
    document_id: str
    document_title: str
    locator: str
    text: str
    method: str


@router.post("/api/ask", response_model=Answer)
def ask_kuki(body: AskRequest, library: Library = Depends(get_library), llm: OllamaClient = Depends(get_llm)) -> Answer:
    return ask(library, llm, body.question, body.document_ids)


@router.get("/api/search", response_model=list[SearchHit])
def search(
    q: str, document_id: str | None = None, library: Library = Depends(get_library), llm: OllamaClient = Depends(get_llm)
) -> list[SearchHit]:
    """Search across the library; powers the command palette in the UI."""
    hits = library.search(q[:300], llm, [document_id] if document_id else None, k=10)
    return [
        SearchHit(
            segment_id=h.passage.segment_id,
            document_id=h.passage.document_id,
            document_title=h.passage.document_title,
            locator=h.passage.locator,
            text=h.passage.text[:400],
            method=h.method,
        )
        for h in hits
    ]
