"""Embedding storage and cosine similarity.

Embeddings are stored in SQLite as raw float32 bytes. For a student's library
(thousands of segments, not millions) brute-force cosine similarity in numpy
takes milliseconds, so there is no need for a vector database.
"""

from __future__ import annotations

import numpy as np


def to_blob(vector: list[float]) -> bytes:
    return np.asarray(vector, dtype=np.float32).tobytes()


def from_blob(blob: bytes) -> np.ndarray:
    return np.frombuffer(blob, dtype=np.float32)


def cosine_scores(query: list[float], matrix: np.ndarray) -> np.ndarray:
    """Cosine similarity of `query` against each row of `matrix`."""
    if matrix.size == 0:
        return np.zeros(0, dtype=np.float32)
    q = np.asarray(query, dtype=np.float32)
    q_norm = np.linalg.norm(q) or 1.0
    row_norms = np.linalg.norm(matrix, axis=1)
    row_norms[row_norms == 0] = 1.0  # avoid dividing by zero for empty vectors
    return (matrix @ q) / (row_norms * q_norm)
