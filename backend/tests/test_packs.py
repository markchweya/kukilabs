import pytest

from kuki import db
from kuki.config import Settings
from kuki.library import Library
from kuki.llm import OllamaClient
from kuki.study.packs import generate_pack, load_pack
from tests.fake_ollama import FakeOllama

NOTES = """# Uninformed search
BFS explores level by level using a queue. DFS goes deep first using a stack.

# Informed search
A heuristic estimates the cost to the goal. A* expands the node with the lowest f(n) = g(n) + h(n).
For example, straight-line distance is a heuristic for road maps.
"""


@pytest.fixture()
def setup(settings):
    library = Library(db.connect(settings.db_path), settings)
    doc_id = library.create_document(title="Week 4 Search", filename="w4.md", kind="text")
    path = library.upload_path(doc_id, "w4.md")
    path.write_text(NOTES)
    library.ingest_file(doc_id, path)
    fake = FakeOllama()
    llm = OllamaClient(settings.ollama_host, transport=fake.transport())
    return library, fake, llm, doc_id


DRAFT = {
    "concepts": [
        {"term": "Heuristic", "explanation": "An estimate of cost to the goal.", "sources": ["S2"]},
        {"term": "heuristic", "explanation": "duplicate", "sources": ["S2"]},
        {"term": "Quantum search", "explanation": "Made up.", "sources": ["S42"]},
    ],
    "key_points": [{"point": "BFS uses a queue.", "sources": ["S1"]}],
    "examples": [{"title": "Road maps", "explanation": "Straight-line distance.", "sources": ["S2"]}],
    "common_mistakes": [{"mistake": "DFS finds shortest paths", "correction": "BFS does, on unweighted graphs", "sources": []}],
}


def test_ai_pack_resolves_citations_and_drops_ungrounded(setup):
    library, fake, llm, doc_id = setup
    fake.respond("StudyPackDraft", DRAFT)
    fake.respond("PackSummaryDraft", {"title": "Search Algorithms", "overview": "How agents search."})

    pack = generate_pack(library, llm, doc_id)
    assert pack.mode == "ai" and pack.title == "Search Algorithms"
    # Duplicate collapsed; invented S42 citation left it ungrounded, so dropped in notes-only mode.
    assert [c.term for c in pack.concepts] == ["Heuristic"]
    assert pack.concepts[0].citations[0].locator == "Section: Informed search"
    assert pack.common_mistakes == []  # no sources -> dropped
    assert load_pack(library, doc_id) == pack


def test_fill_gaps_keeps_unsourced_items_flagged(setup):
    library, fake, llm, doc_id = setup
    fake.respond("StudyPackDraft", DRAFT)
    fake.respond("PackSummaryDraft", {"title": "T", "overview": "O"})
    pack = generate_pack(library, llm, doc_id, knowledge="fill_gaps")
    assert len(pack.common_mistakes) == 1
    assert pack.common_mistakes[0].grounded is False


def test_offline_falls_back_to_extractive(setup):
    library, fake, llm, doc_id = setup
    fake.down = True
    pack = generate_pack(library, llm, doc_id)
    assert pack.mode == "extractive"
    assert "offline" in pack.notice
    assert pack.key_points and all(p.grounded for p in pack.key_points)


def test_long_documents_are_batched(setup, settings):
    library, fake, llm, doc_id = setup
    small = Settings(**{**settings.__dict__, "num_ctx": 2048})
    library.settings = small
    library.save_segments(doc_id, [__import__("kuki.ingest", fromlist=["Segment"]).Segment(f"Slide {i}", "x " * 900) for i in range(4)])
    fake.respond("StudyPackDraft", {"concepts": [], "key_points": [], "examples": [], "common_mistakes": []})
    generate_pack(library, llm, doc_id)
    pack_calls = [b for path, b in fake.requests if path == "/api/chat" and b["format"]["title"] == "StudyPackDraft"]
    assert len(pack_calls) > 1
