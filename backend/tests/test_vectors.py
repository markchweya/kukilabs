import numpy as np

from kuki.search.vectors import cosine_scores, from_blob, to_blob


def test_blob_round_trip():
    assert np.allclose(from_blob(to_blob([0.5, -1.25, 3.0])), [0.5, -1.25, 3.0])


def test_cosine_scores():
    matrix = np.array([[1, 0], [0, 1], [1, 1], [0, 0]], dtype=np.float32)
    scores = cosine_scores([1, 0], matrix)
    assert np.allclose(scores, [1.0, 0.0, 1 / np.sqrt(2), 0.0])


def test_cosine_empty_matrix():
    assert cosine_scores([1.0], np.zeros((0, 1), dtype=np.float32)).size == 0
