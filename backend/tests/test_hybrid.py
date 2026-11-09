import numpy as np

from kuki.search.hybrid import Passage, rank


def passage(i, text, vec=None):
    return Passage(i, "d", "Doc", f"Slide {i}", text, None if vec is None else np.array(vec, dtype=np.float32))


def test_keyword_only_when_no_vectors():
    ps = [passage(1, "queues and stacks"), passage(2, "binary search trees"), passage(3, "hash tables")]
    hits = rank(ps, "binary trees", query_vector=None, k=2)
    assert hits[0].passage.segment_id == 2
    assert hits[0].method == "keyword"
    assert len(hits) == 1  # passages with no keyword overlap are not returned


def test_semantic_finds_paraphrase_without_shared_words():
    ps = [passage(1, "FIFO structure", [1, 0]), passage(2, "LIFO structure", [0, 1])]
    hits = rank(ps, "first in first out", query_vector=[0.9, 0.1], k=1)
    assert hits[0].passage.segment_id == 1
    assert hits[0].method == "semantic"


def test_hybrid_agreement_ranks_first():
    ps = [
        passage(1, "dijkstra shortest path", [1, 0]),
        passage(2, "dijkstra biography", [0, 1]),
        passage(3, "shortest route between nodes", [0.9, 0.1]),
    ]
    hits = rank(ps, "dijkstra shortest path", query_vector=[1, 0], k=3)
    assert hits[0].passage.segment_id == 1
    assert hits[0].method == "hybrid"


def test_empty():
    assert rank([], "q", None) == []
