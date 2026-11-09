import pytest

from kuki import db
from kuki.library import Library, NotFound


@pytest.fixture()
def library(settings):
    return Library(db.connect(settings.db_path), settings)


def test_create_list_get(library):
    a = library.create_document(title="Week 1", filename="w1.pdf", kind="pdf")
    b = library.create_document(title="Week 2", filename="w2.pptx", kind="slides")
    docs = library.list_documents()
    assert [d.id for d in docs] == [b, a]  # newest first
    doc = library.get_document(a)
    assert doc.status == "processing" and doc.segment_count == 0


def test_delete_removes_upload(library):
    doc_id = library.create_document(title="T", filename="t.txt", kind="text")
    stored = library.upload_path(doc_id, "t.txt")
    stored.write_text("hello")
    library.delete_document(doc_id)
    assert not stored.exists()
    with pytest.raises(NotFound):
        library.get_document(doc_id)


def test_ingest_success(library):
    doc_id = library.create_document(title="Notes", filename="n.md", kind="text")
    path = library.upload_path(doc_id, "n.md")
    path.write_text("# Stacks\nLIFO.\n\n# Queues\nFIFO.")
    library.ingest_file(doc_id, path)
    doc = library.get_document(doc_id)
    assert doc.status == "ready" and doc.segment_count == 2
    assert [r["locator"] for r in library.segments(doc_id)] == ["Section: Stacks", "Section: Queues"]


def test_ingest_failure_is_recorded_not_raised(library):
    doc_id = library.create_document(title="Empty", filename="e.txt", kind="text")
    path = library.upload_path(doc_id, "e.txt")
    path.write_text("")
    library.ingest_file(doc_id, path)
    doc = library.get_document(doc_id)
    assert doc.status == "failed"
    assert "No readable text" in doc.error


def _ready_doc(library, text):
    doc_id = library.create_document(title="Algorithms", filename="a.md", kind="text")
    path = library.upload_path(doc_id, "a.md")
    path.write_text(text)
    library.ingest_file(doc_id, path)
    return doc_id


def test_embed_then_hybrid_search(library, settings):
    from kuki.llm import OllamaClient
    from tests.fake_ollama import FakeOllama

    llm = OllamaClient(settings.ollama_host, transport=FakeOllama().transport())
    doc_id = _ready_doc(library, "# BFS\nUses a queue.\n\n# DFS\nUses a stack.\n\n# Dijkstra\nShortest paths.")
    assert library.embed_missing(llm) == 3
    assert library.embed_missing(llm) == 0  # nothing left to do

    hits = library.search("which algorithm uses a stack", llm, [doc_id], k=1)
    assert hits[0].passage.locator == "Section: DFS"
    assert hits[0].method == "hybrid"


def test_search_falls_back_to_keywords_when_ollama_down(library, settings):
    from kuki.llm import OllamaClient
    from tests.fake_ollama import FakeOllama

    fake = FakeOllama()
    llm = OllamaClient(settings.ollama_host, transport=fake.transport())
    _ready_doc(library, "# BFS\nUses a queue.\n\n# DFS\nUses a stack.")
    library.embed_missing(llm)
    fake.down = True
    assert library.embed_missing(llm) == 0  # nothing pending; and no crash
    hits = library.search("stack", llm, k=1)
    assert hits[0].passage.locator == "Section: DFS"
    assert hits[0].method == "keyword"
