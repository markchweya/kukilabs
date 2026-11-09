from kuki.search.hybrid import Passage
from kuki.study.sources import SourceSet, batch_by_size


def p(i, text="text"):
    return Passage(i, "d1", "Week 4", f"Slide {i}", text)


def test_render_and_resolve():
    sources = SourceSet.number([p(10, "BFS uses a queue"), p(11, "DFS uses a stack")])
    rendered = sources.render()
    assert "[S1] (Week 4, Slide 10)\nBFS uses a queue" in rendered
    cites = sources.resolve(["S2", "[s1]", "S2", "S99"])  # dupes, brackets, case, made-up tag
    assert [c.segment_id for c in cites] == [11, 10]
    assert cites[0].locator == "Slide 11"


def test_numbering_offset_keeps_tags_unique_across_batches():
    assert list(SourceSet.number([p(1), p(2)], start=5).by_tag) == ["S5", "S6"]


def test_batch_by_size():
    batches = batch_by_size([p(i, "x" * 400) for i in range(5)], max_chars=1000)
    assert [len(b) for b in batches] == [2, 2, 1]
