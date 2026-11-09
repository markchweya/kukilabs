"""Okapi BM25 keyword ranking.

This is Kuki's backup search: it needs no model at all, so search keeps
working when Ollama is off or the embedding model is not installed. It is also
blended into hybrid search because exact terms ("Dijkstra", "O(n log n)")
matter a lot in study material and embeddings can blur them.
"""

from __future__ import annotations

import math
import re
from collections import Counter

# A deliberately small stop-word list: removing too much hurts technical text
# ("not", "no", "all" can be the whole point of a sentence).
STOP_WORDS = frozenset(
    "a an and are as at be by for from has have in is it its of on or that the this to was were will with".split()
)
# Keeps hyphenated words (k-means) and trailing operators (A*, C++) intact.
_TOKEN = re.compile(r"[a-z0-9]+(?:['\-][a-z0-9]+)*[*+]*")


def tokenize(text: str) -> list[str]:
    return [t for t in _TOKEN.findall(text.lower()) if t not in STOP_WORDS]


class BM25:
    def __init__(self, documents: list[str], k1: float = 1.5, b: float = 0.75):
        self.k1, self.b = k1, b
        self.docs = [Counter(tokenize(d)) for d in documents]
        self.lengths = [sum(c.values()) for c in self.docs]
        self.avg_len = (sum(self.lengths) / len(self.lengths)) if self.lengths else 0.0
        df: Counter[str] = Counter()
        for counts in self.docs:
            df.update(counts.keys())
        n = len(self.docs)
        # The "+1" inside the log keeps IDF positive for very common terms.
        self.idf = {term: math.log(1 + (n - freq + 0.5) / (freq + 0.5)) for term, freq in df.items()}

    def scores(self, query: str) -> list[float]:
        terms = tokenize(query)
        out = []
        for counts, length in zip(self.docs, self.lengths):
            score = 0.0
            norm = self.k1 * (1 - self.b + self.b * length / (self.avg_len or 1))
            for term in terms:
                tf = counts.get(term)
                if tf:
                    score += self.idf[term] * tf * (self.k1 + 1) / (tf + norm)
            out.append(score)
        return out
