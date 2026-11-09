"""Hybrid ranking: keyword (BM25) + semantic (embeddings), fused by rank.

BM25 scores and cosine similarities live on different scales, so instead of
adding them we use Reciprocal Rank Fusion (Cormack et al., 2009): each list
contributes 1 / (k + rank). It needs no tuning and is robust when one of the
two signals is weak or missing entirely.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from kuki.search.bm25 import BM25
from kuki.search.vectors import cosine_scores

RRF_K = 60  # the constant recommended in the original RRF paper


@dataclass(frozen=True)
class Passage:
    segment_id: int
    document_id: str
    document_title: str
    locator: str
    text: str
    embedding: np.ndarray | None = None


@dataclass(frozen=True)
class Hit:
    passage: Passage
    score: float
    method: str  # "hybrid", "keyword" or "semantic"


def rank(passages: list[Passage], query: str, query_vector: list[float] | None, k: int = 6) -> list[Hit]:
    """Return the `k` best passages for `query`.

    `query_vector` is None when embeddings are unavailable; ranking then
    degrades gracefully to keyword-only.
    """
    if not passages:
        return []

    keyword = BM25([p.text for p in passages]).scores(query)
    rankings = [_order(keyword, keep_zero=False)]

    embedded = [i for i, p in enumerate(passages) if p.embedding is not None]
    if query_vector is not None and embedded:
        matrix = np.stack([passages[i].embedding for i in embedded])
        semantic = np.full(len(passages), -1.0, dtype=np.float32)
        semantic[embedded] = cosine_scores(query_vector, matrix)
        rankings.append(_order(semantic.tolist(), keep_zero=True, only=embedded))

    fused: dict[int, float] = {}
    for ranking in rankings:
        for position, index in enumerate(ranking):
            fused[index] = fused.get(index, 0.0) + 1.0 / (RRF_K + position + 1)

    method = "hybrid" if len(rankings) == 2 else "keyword"
    if len(rankings) == 2 and not rankings[0]:
        method = "semantic"  # no keyword overlap at all; meaning carried it
    best = sorted(fused, key=fused.__getitem__, reverse=True)[:k]
    return [Hit(passages[i], fused[i], method) for i in best]


def _order(scores: list[float], keep_zero: bool, only: list[int] | None = None) -> list[int]:
    """Indices sorted by descending score, optionally dropping non-matches."""
    candidates = only if only is not None else range(len(scores))
    kept = [i for i in candidates if keep_zero or scores[i] > 0]
    return sorted(kept, key=lambda i: scores[i], reverse=True)
