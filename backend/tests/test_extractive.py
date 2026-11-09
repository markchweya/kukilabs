from kuki.search.hybrid import Passage
from kuki.study.extractive import extractive_concepts, extractive_examples, extractive_points


def p(i, text):
    return Passage(i, "d", "Week 4", f"Slide {i}", text)


PASSAGES = [
    p(1, "Heuristic: an estimate of the cost from a node to the goal.\nAdmissible: never overestimates the true cost."),
    p(2, "A queue is a first-in first-out data structure used by BFS. It is simple."),
    p(3, "Greedy search can get stuck. For example, it may follow a dead end that looks close to the goal."),
]


def test_concepts_from_colon_lines_and_is_sentences():
    concepts = extractive_concepts(PASSAGES)
    terms = [c.term for c in concepts]
    assert "Heuristic" in terms and "Admissible" in terms and "queue" in terms
    assert all(c.grounded for c in concepts)


def test_points_and_examples_are_cited():
    points = extractive_points(PASSAGES)
    assert points[0].citations[0].locator == "Slide 1"
    examples = extractive_examples(PASSAGES)
    assert examples[0].citations[0].locator == "Slide 3"
    assert "dead end" in examples[0].explanation
