"""Weak spots: what a student keeps getting wrong, across all their quizzes.

A single wrong answer is noise; the same concept or the same *kind* of mistake
showing up again is a signal worth revising.
"""

from __future__ import annotations

from pydantic import BaseModel

from kuki.library import Library

# A concept is "mastered" once the latest attempt scores at least this.
MASTERY_SCORE = 80


class ConceptProgress(BaseModel):
    concept: str
    document_id: str
    document_title: str
    attempts: int
    latest_score: int
    best_score: int
    latest_misconception: str | None
    status: str  # "weak", "improving", "mastered"


class Insights(BaseModel):
    concepts: list[ConceptProgress]
    mistake_patterns: dict[str, int]  # misconception_type -> count
    total_attempts: int


def build_insights(library: Library, document_id: str | None = None) -> Insights:
    where, params = ("WHERE q.document_id = ?", (document_id,)) if document_id else ("", ())
    rows = library.conn.execute(
        f"""
        SELECT q.concept, q.document_id, d.title, a.score, a.misconception, a.misconception_type
        FROM attempts a
        JOIN questions q ON q.id = a.question_id
        JOIN documents d ON d.id = q.document_id
        {where}
        ORDER BY a.created_at, a.id
        """,
        params,
    ).fetchall()

    by_concept: dict[tuple[str, str], list] = {}
    patterns: dict[str, int] = {}
    for r in rows:
        by_concept.setdefault((r[1], r[0].strip().lower()), []).append(r)
        if r[5] and r[5] != "none":
            patterns[r[5]] = patterns.get(r[5], 0) + 1

    progress = []
    for attempts in by_concept.values():
        latest = attempts[-1]
        best = max(a[3] for a in attempts)
        if latest[3] >= MASTERY_SCORE:
            status = "mastered"
        elif len(attempts) > 1 and latest[3] > attempts[-2][3]:
            status = "improving"
        else:
            status = "weak"
        progress.append(ConceptProgress(
            concept=latest[0],
            document_id=latest[1],
            document_title=latest[2],
            attempts=len(attempts),
            latest_score=latest[3],
            best_score=best,
            latest_misconception=latest[4] or None,
            status=status,
        ))

    # Weakest first: that's what the student should revise next.
    order = {"weak": 0, "improving": 1, "mastered": 2}
    progress.sort(key=lambda p: (order[p.status], p.latest_score))
    return Insights(
        concepts=progress,
        mistake_patterns=dict(sorted(patterns.items(), key=lambda kv: -kv[1])),
        total_attempts=len(rows),
    )
