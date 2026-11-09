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
