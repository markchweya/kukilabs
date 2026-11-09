"""Quiz generation and misconception-aware grading."""

from __future__ import annotations

import json
import logging
import random
import re
import sqlite3

from kuki.db import transaction
from kuki.library import Library, NotFound
from kuki.llm import OllamaClient, OllamaError
from kuki.search.hybrid import Passage
from kuki.study import prompts
from kuki.study.extractive import extractive_concepts
from kuki.study.packs import source_budget
from kuki.search.bm25 import tokenize
from kuki.study.quiz_models import ClaimCheck, Grade, GradeDraft, GradeResult, QuizDraft, Question
from kuki.study.sources import Citation, SourceSet
from kuki.study.text import clean

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
            (
                short_concept(q.concept),
                clean(q.question),
                clean(q.ideal_answer),
                [clean(k) for k in q.key_ideas if clean(k)],
                sources.resolve(q.sources, f"{q.question} {q.ideal_answer}"),
            )
            for q in draft.questions[:count]
        ]
        # Questions the model could not tie to the notes are not worth asking.
        rows = [r for r in rows if r[4]]
    except OllamaError as exc:
        log.info("AI quiz failed (%s); building recall questions instead.", exc)
        rows = _offline_questions(passages, count)

    return [_store_question(library.conn, doc_id, *row) for row in rows]


_LEADING_VERBS = re.compile(r"^(explaining|explain|comparing|compare|applying|apply|understanding|the concept of)\s+(the\s+)?(concept of\s+)?", re.I)


def short_concept(text: str, max_words: int = 6) -> str:
    """Keep concept labels short enough to group on the Weak spots page.

    Small models sometimes write a sentence ("Explaining the difference between
    BFS and DFS") despite the prompt; strip the leading verb and cap the length.
    """
    text = _LEADING_VERBS.sub("", clean(text)).strip()
    words = text.split()[:max_words]
    # Don't end a cut-off label on a connector ("... BFS and").
    while words and words[-1].lower() in {"and", "or", "of", "the", "in", "between", "vs", "to", "a", "for", "with"}:
        words.pop()
    text = " ".join(words)
    return (text[:1].upper() + text[1:]) if text else "General"


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
    claims = split_claims(answer)

    try:
        draft = llm.chat_json(
            library.settings.chat_model,
            [
                {"role": "system", "content": prompts.TUTOR},
                {"role": "user", "content": prompts.grade(row["prompt"], row["ideal_answer"], key_ideas, source_text, answer, claims)},
            ],
            GradeDraft,
            temperature=0.1,  # grading should be consistent, not creative
            num_ctx=library.settings.num_ctx,
        )
        result = aggregate_grade(draft, claims, key_ideas)
        mode = "ai"
    except OllamaError as exc:
        log.info("AI grading failed (%s); using keyword overlap.", exc)
        result = keyword_grade(answer, key_ideas, row["ideal_answer"])
        mode = "keyword"

    with transaction(library.conn):
        cur = library.conn.execute(
            "INSERT INTO attempts(question_id, answer, verdict, score, misconception, misconception_type, feedback)"
            " VALUES (?, ?, ?, ?, ?, ?, ?)",
            (question_id, answer, result.verdict, result.score, result.misconception, result.misconception_type, result.model_dump_json()),
        )
    return Grade(
        attempt_id=cur.lastrowid,
        question_id=question_id,
        ideal_answer=row["ideal_answer"],
        key_ideas=key_ideas,
        citations=citations,
        mode=mode,
        **result.model_dump(),
    )


# Each contradicted claim costs this many points on top of missing key ideas.
CONTRADICTION_PENALTY = 30


def aggregate_grade(draft: GradeDraft, claims: list[str], key_ideas: list[str]) -> GradeResult:
    """Turn per-claim checks into a verdict, score and feedback, in code.

    Guards against what a real 3B model did in testing:
    * praising things the student never said -> claims come from the
      student's own answer (split in code), never from the model;
    * flagging a correct statement as a misconception -> a misconception now
      requires a claim the model marked as contradicted by the lecture;
    * inconsistent scores -> the score is computed from key-idea coverage
      and contradictions, not chosen by the model.
    """
    # A model may return more or fewer checks than claims; pair what lines up.
    pairs = list(zip(claims, draft.checks))
    supported = [c for c, chk in pairs if chk.status == "supported"]
    contradicted = [(c, chk) for c, chk in pairs if chk.status == "contradicted"]
    wanted = {_norm(k): k for k in key_ideas}
    missing = [wanted[_norm(m)] for m in draft.missing_ideas if _norm(m) in wanted]
    # Backstop: a 3B model listed "BFS uses a FIFO queue" as missing from an
    # answer that said exactly that. An idea whose words are all in the answer
    # is not missing.
    answer_terms = set(tokenize(" ".join(claims)))
    missing = [m for m in dict.fromkeys(missing) if not _covered(m, answer_terms)]

    coverage = (len(key_ideas) - len(missing)) / len(key_ideas) if key_ideas else (1.0 if supported else 0.0)
    score = round(100 * coverage) - CONTRADICTION_PENALTY * len(contradicted)
    if not claims:
        score = 0
    score = max(0, min(100, score))

    if contradicted:
        claim, check = contradicted[0]
        correction = tidy_correction(check.correction) or "the lecture says otherwise"
        misconception = f"You said “{claim}”, but {_lower_first(correction)}"
        kind = draft.misconception_type if draft.misconception_type in ("confused_concepts", "factual_error", "overgeneralization") else "factual_error"
    elif missing:
        misconception = "Your answer leaves out: " + "; ".join(missing)
        kind = "missing_step" if supported else ("off_topic" if draft.misconception_type == "off_topic" else "vague")
    else:
        misconception, kind = "", "none"

    if not contradicted and not missing and claims:
        verdict = "correct"
    elif not supported or score < 20:
        verdict = "incorrect"
    else:
        verdict = "partial"

    return GradeResult(
        verdict=verdict,
        score=score,
        got_right=supported,
        misconception=misconception,
        misconception_type=kind,
        nudge="" if verdict == "correct" else clean(draft.nudge),
        explanation=clean(draft.explanation),
    )


# Split only at sentence ends and semicolons. Splitting on "and", "but" or
# "because" leaves fragments with no subject ("may return a longer path").
_CLAIM_SPLIT = re.compile(r"(?<=[.!?])\s+|;\s*")
MAX_CLAIMS = 8


def split_claims(answer: str) -> list[str]:
    """Split a student's answer into short statements the grader can check one by one."""
    parts = [clean(p).rstrip(".;!?") for p in _CLAIM_SPLIT.split(answer) if p and p.strip()]
    claims: list[str] = []
    carry = ""
    for part in parts:
        if not part:
            continue
        # Fragments under three words ("Yes", "So") join a neighbouring claim.
        if len(part.split()) < 3:
            if claims:
                claims[-1] = f"{claims[-1]}, {part[0].lower() + part[1:]}"
            else:
                carry = f"{carry} {part}".strip()
            continue
        claims.append(f"{carry}, {part}" if carry else part)
        carry = ""
    if carry:
        claims.append(carry)
    if len(claims) > MAX_CLAIMS:
        claims = claims[: MAX_CLAIMS - 1] + [" ".join(claims[MAX_CLAIMS - 1 :])]
    return claims


def _covered(idea: str, answer_terms: set[str], threshold: float = 0.8) -> bool:
    terms = set(tokenize(idea))
    return bool(terms) and len(terms & answer_terms) / len(terms) >= threshold


_SOURCE_NOTE = re.compile(r"\s*\((?:lecture )?sources?:[^)]*\)\s*", re.I)


def tidy_correction(text: str, max_sentences: int = 2) -> str:
    """Normalise a model-written correction: no placeholders, no source notes, two sentences at most."""
    text = _SOURCE_NOTE.sub(" ", clean(text)).strip()
    if text.lower().rstrip(".") in {"", "none", "n/a", "na", "null"}:
        return ""
    sentences = re.split(r"(?<=[.!?])\s+", text)
    return " ".join(sentences[:max_sentences]).strip()


def _lower_first(text: str) -> str:
    """Lowercase a sentence's first letter to continue a sentence, unless it starts an acronym (DFS, A*)."""
    first = text.split(" ", 1)[0]
    if len(first) > 1 and not first[1:].islower():
        return text
    return text[:1].lower() + text[1:]


def _norm(text: str) -> str:
    return " ".join(tokenize(text))


def _cited_text(library: Library, citations: list[Citation]) -> str:
    """Full text of the segments a question was built from, for the grader."""
    if not citations:
        return "(none)"
    ids = [c.segment_id for c in citations]
    rows = library.conn.execute(
        f"SELECT locator, text FROM segments WHERE id IN ({','.join('?' * len(ids))})", ids
    ).fetchall()
    return "\n\n".join(f"({r[0]}) {r[1][:1800]}" for r in rows) or "(none)"


def keyword_grade(answer: str, key_ideas: list[str], ideal_answer: str) -> GradeResult:
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
    return GradeResult(
        verdict=verdict,
        score=score,
        got_right=covered,
        misconception=("Your answer may be missing: " + "; ".join(missing)) if missing else "",
        misconception_type="none" if not missing else "missing_step" if covered else "vague",
        nudge=f"How would you explain {missing[0].rstrip('.').lower()}?" if missing else "Can you give an example?",
        explanation=ideal_answer,
    )
