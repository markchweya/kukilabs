"""Quiz generation and misconception-aware grading."""

from __future__ import annotations

import json
import logging
import random
import sqlite3

from kuki.db import transaction
from kuki.library import Library, NotFound
from kuki.llm import OllamaClient, OllamaError
from kuki.search.hybrid import Passage
from kuki.study import prompts
from kuki.study.extractive import extractive_concepts
from kuki.study.packs import source_budget
from kuki.search.bm25 import tokenize
from kuki.study.quiz_models import Grade, GradeDraft, QuizDraft, Question
from kuki.study.sources import Citation, SourceSet

log = logging.getLogger(__name__)


def spread_sample(passages: list[Passage], max_chars: int, seed: int | None = None) -> list[Passage]:
    """Pick passages from across the whole document up to a size budget.

    Quizzing only the first slides would be useless, so we shuffle, take what
    fits, then restore reading order so the model sees coherent context.
    """
    rng = random.Random(seed)
    order = list(range(len(passages)))
    rng.shuffle(order)
    chosen, size = [], 0
    for i in order:
        if size + len(passages[i].text) > max_chars and chosen:
            continue
        chosen.append(i)
        size += len(passages[i].text)
    return [passages[i] for i in sorted(chosen)]


def generate_quiz(library: Library, llm: OllamaClient, doc_id: str, count: int = 5) -> list[Question]:
    library.get_document(doc_id)
    passages = library.passages([doc_id])
    if not passages:
        raise NotFound("This document has no readable text yet.")
    count = max(1, min(count, 10))

    sources = SourceSet.number(spread_sample(passages, source_budget(library.settings)))
    try:
        draft = llm.chat_json(
            library.settings.chat_model,
            [
                {"role": "system", "content": prompts.TUTOR},
                {"role": "user", "content": prompts.quiz(sources.render(), count)},
            ],
            QuizDraft,
            temperature=0.5,  # a little variety so regenerating gives new questions
            num_ctx=library.settings.num_ctx,
        )
        rows = [
            (q.concept, q.question, q.ideal_answer, q.key_ideas, sources.resolve(q.sources))
            for q in draft.questions[:count]
        ]
        # Questions the model could not tie to the notes are not worth asking.
        rows = [r for r in rows if r[4]]
    except OllamaError as exc:
        log.info("AI quiz failed (%s); building recall questions instead.", exc)
        rows = _offline_questions(passages, count)

    return [_store_question(library.conn, doc_id, *row) for row in rows]


def _offline_questions(passages: list[Passage], count: int):
    """Without a model: 'explain this term' questions from extracted definitions."""
    out = []
    for c in extractive_concepts(passages, limit=count):
        ideas = [c.explanation]
        out.append((c.term, f"In your own words, what is {c.term} and why does it matter?", c.explanation, ideas, c.citations))
    return out


def _store_question(conn: sqlite3.Connection, doc_id, concept, prompt, ideal, ideas, citations: list[Citation]) -> Question:
    with transaction(conn):
        cur = conn.execute(
            "INSERT INTO questions(document_id, concept, prompt, ideal_answer, key_ideas, citations) VALUES (?, ?, ?, ?, ?, ?)",
            (doc_id, concept, prompt, ideal, json.dumps(ideas), json.dumps([c.model_dump() for c in citations])),
        )
    return Question(id=cur.lastrowid, document_id=doc_id, concept=concept, prompt=prompt, citations=citations)


def list_questions(library: Library, doc_id: str) -> list[Question]:
    rows = library.conn.execute(
        "SELECT id, document_id, concept, prompt, citations FROM questions WHERE document_id = ? ORDER BY id DESC",
        (doc_id,),
    )
    return [
        Question(id=r[0], document_id=r[1], concept=r[2], prompt=r[3], citations=json.loads(r[4])) for r in rows
    ]


# ---- grading ---------------------------------------------------------------

MAX_ANSWER_CHARS = 4000


def grade_answer(library: Library, llm: OllamaClient, question_id: int, answer: str) -> Grade:
    row = library.conn.execute(
        "SELECT q.id, q.prompt, q.ideal_answer, q.key_ideas, q.citations FROM questions q WHERE q.id = ?",
        (question_id,),
    ).fetchone()
    if row is None:
        raise NotFound(f"No question with id {question_id}")
    answer = answer.strip()[:MAX_ANSWER_CHARS]
    if not answer:
        raise ValueError("Write an answer first.")

    key_ideas: list[str] = json.loads(row["key_ideas"])
    citations = [Citation.model_validate(c) for c in json.loads(row["citations"])]
    source_text = _cited_text(library, citations)

    try:
        draft = llm.chat_json(
            library.settings.chat_model,
            [
                {"role": "system", "content": prompts.TUTOR},
                {"role": "user", "content": prompts.grade(row["prompt"], row["ideal_answer"], key_ideas, source_text, answer)},
            ],
            GradeDraft,
            temperature=0.1,  # grading should be consistent, not creative
            num_ctx=library.settings.num_ctx,
        )
        mode = "ai"
    except OllamaError as exc:
        log.info("AI grading failed (%s); using keyword overlap.", exc)
        draft = keyword_grade(answer, key_ideas, row["ideal_answer"])
        mode = "keyword"

    with transaction(library.conn):
        cur = library.conn.execute(
            "INSERT INTO attempts(question_id, answer, verdict, score, misconception, misconception_type, feedback)"
            " VALUES (?, ?, ?, ?, ?, ?, ?)",
            (question_id, answer, draft.verdict, draft.score, draft.misconception, draft.misconception_type, draft.model_dump_json()),
        )
    return Grade(
        attempt_id=cur.lastrowid,
        question_id=question_id,
        ideal_answer=row["ideal_answer"],
        key_ideas=key_ideas,
        citations=citations,
        mode=mode,
        **draft.model_dump(),
    )


def _cited_text(library: Library, citations: list[Citation]) -> str:
    """Full text of the segments a question was built from, for the grader."""
    if not citations:
        return "(none)"
    ids = [c.segment_id for c in citations]
    rows = library.conn.execute(
        f"SELECT locator, text FROM segments WHERE id IN ({','.join('?' * len(ids))})", ids
    ).fetchall()
    return "\n\n".join(f"({r[0]}) {r[1][:1800]}" for r in rows) or "(none)"


def keyword_grade(answer: str, key_ideas: list[str], ideal_answer: str) -> GradeDraft:
    """Offline backup grader: how many key ideas does the answer touch?

    Crude but honest. It never claims to have found a misconception it cannot
    see; it just shows which ideas seem to be missing.
    """
    answer_terms = set(tokenize(answer))
    covered, missing = [], []
    for idea in key_ideas:
        terms = set(tokenize(idea))
        overlap = len(terms & answer_terms) / max(1, len(terms))
        (covered if overlap >= 0.4 else missing).append(idea)

    score = round(100 * len(covered) / max(1, len(key_ideas)))
    verdict = "correct" if score >= 80 else "partial" if score >= 34 else "incorrect"
    return GradeDraft(
        verdict=verdict,
        score=score,
        got_right=covered,
        misconception=("Your answer may be missing: " + "; ".join(missing)) if missing else "",
        misconception_type="none" if not missing else "missing_step" if covered else "vague",
        nudge=f"How would you explain {missing[0].rstrip('.').lower()}?" if missing else "Can you give an example?",
        explanation=ideal_answer,
    )
