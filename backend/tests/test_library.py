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
