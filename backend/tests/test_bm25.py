from kuki.search.bm25 import BM25, tokenize


def test_tokenize_keeps_technical_terms():
    assert tokenize("The A* search, O(n) and k-means!") == ["a*", "search", "o", "n", "k-means"]


def test_rare_exact_term_wins():
    docs = [
        "search algorithms explore a state space",
        "breadth first search uses a queue",
        "dijkstra finds shortest paths with nonnegative weights",
    ]
    scores = BM25(docs).scores("dijkstra shortest path")
    assert scores.index(max(scores)) == 2


def test_empty_corpus_and_query():
    assert BM25([]).scores("anything") == []
    assert BM25(["text"]).scores("the") == [0.0]
