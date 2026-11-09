"""Ask Kuki: answer a question from the student's own notes, with citations."""

from __future__ import annotations

import logging
import re
from typing import Literal

from pydantic import BaseModel, Field

from kuki.library import Library
from kuki.llm import OllamaClient, OllamaError
from kuki.study import prompts
from kuki.study.sources import Citation, SourceSet
from kuki.study.text import clean

log = logging.getLogger(__name__)


class AnswerDraft(BaseModel):
    # Order matters: the model writes its answer before deciding `found`. With
    # `found` first, a real 3B model set it true and then wrote "the sources
    # do not mention this".
    answer: str
    sources: list[str]
    found: bool = Field(description="True only if the sources contain the answer")


# Phrases a model uses when the notes don't have the answer, as a backstop
# for an inconsistent `found` flag.
_NOT_FOUND = re.compile(
    r"(not (explicitly )?(mentioned|stated|covered|provided|included|given)|"
    r"(do|does) not (mention|say|provide|include|cover|contain)|"
    r"no information (about|on)|isn't in (the|your) (sources|notes)|not in (the|your) (sources|notes))",
    re.I,
)


class Answer(BaseModel):
    question: str
    answer: str
    found: bool
    citations: list[Citation]
    mode: Literal["ai", "search"]


def ask(library: Library, llm: OllamaClient, question: str, document_ids: list[str] | None = None) -> Answer:
    question = question.strip()[:1000]
    if not question:
        raise ValueError("Ask a question first.")

    hits = library.search(question, llm, document_ids, k=6)
    if not hits:
        return Answer(question=question, answer="I couldn't find anything about that in your notes.", found=False, citations=[], mode="search")

    sources = SourceSet.number([h.passage for h in hits])
    try:
        draft = llm.chat_json(
            library.settings.chat_model,
            [{"role": "system", "content": prompts.TUTOR}, {"role": "user", "content": prompts.ask(question, sources.render())}],
            AnswerDraft,
            num_ctx=library.settings.num_ctx,
        )
        citations = sources.resolve(draft.sources, draft.answer)
        # An answer that claims to be found but cites nothing, or that says the
        # notes don't cover it, is not a found answer.
        found = draft.found and bool(citations) and not _NOT_FOUND.search(draft.answer)
        return Answer(
            question=question,
            answer=clean(draft.answer),
            found=found,
            citations=citations if found else [],
            mode="ai",
        )
    except OllamaError as exc:
        log.info("AI answer failed (%s); returning best passages.", exc)
        top = sources.resolve(list(sources.by_tag)[:3])
        return Answer(
            question=question,
            answer="Kuki's AI is offline, but these parts of your notes look most relevant:",
            found=True,
            citations=top,
            mode="search",
        )
