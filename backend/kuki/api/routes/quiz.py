"""Quiz endpoints: generate questions, submit answers, see weak spots."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from kuki.api.deps import ensure_ready, get_library, get_llm
from kuki.library import Library
from kuki.llm import OllamaClient
from kuki.study.insights import Insights, build_insights
from kuki.study.quiz import generate_quiz, grade_answer, list_questions
from kuki.study.quiz_models import Grade, Question

router = APIRouter(tags=["quiz"])


class QuizRequest(BaseModel):
    count: int = Field(5, ge=1, le=10)


class AnswerRequest(BaseModel):
    answer: str = Field(min_length=1, max_length=4000)


@router.post("/api/documents/{doc_id}/quiz", response_model=list[Question])
def create_quiz(
    doc_id: str,
    body: QuizRequest | None = None,
    library: Library = Depends(get_library),
    llm: OllamaClient = Depends(get_llm),
) -> list[Question]:
    ensure_ready(library, doc_id)
    return generate_quiz(library, llm, doc_id, (body or QuizRequest()).count)


@router.get("/api/documents/{doc_id}/quiz", response_model=list[Question])
def get_questions(doc_id: str, library: Library = Depends(get_library)) -> list[Question]:
    library.get_document(doc_id)
    return list_questions(library, doc_id)


@router.post("/api/questions/{question_id}/answer", response_model=Grade)
def answer_question(
    question_id: int,
    body: AnswerRequest,
    library: Library = Depends(get_library),
    llm: OllamaClient = Depends(get_llm),
) -> Grade:
    return grade_answer(library, llm, question_id, body.answer)


@router.get("/api/insights", response_model=Insights)
def insights(document_id: str | None = None, library: Library = Depends(get_library)) -> Insights:
    return build_insights(library, document_id)
