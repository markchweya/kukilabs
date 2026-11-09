import pytest

from kuki import db
from kuki.library import Library
from kuki.llm import OllamaClient
from kuki.study.ask import ask
from tests.fake_ollama import FakeOllama


@pytest.fixture()
def setup(settings):
    library = Library(db.connect(settings.db_path), settings)
    doc_id = library.create_document(title="DS", filename="d.md", kind="text")
    path = library.upload_path(doc_id, "d.md")
    path.write_text("# Stacks\nA stack is last in, first out.\n\n# Queues\nA queue is first in, first out.")
    library.ingest_file(doc_id, path)
    fake = FakeOllama()
    return library, fake, OllamaClient(settings.ollama_host, transport=fake.transport())


def test_answer_with_citations(setup):
    library, fake, llm = setup
    fake.respond("AnswerDraft", {"found": True, "answer": "LIFO.", "sources": ["S1"]})
    ans = ask(library, llm, "what order does a stack use?")
    assert ans.found and ans.mode == "ai"
    assert ans.citations[0].locator == "Section: Stacks"


def test_found_without_citation_is_not_trusted(setup):
    library, fake, llm = setup
    fake.respond("AnswerDraft", {"found": True, "answer": "Trust me.", "sources": []})
    assert ask(library, llm, "stack order").found is False


def test_offline_returns_passages(setup):
    library, fake, llm = setup
    fake.down = True
    ans = ask(library, llm, "queue")
    assert ans.mode == "search" and ans.citations[0].locator == "Section: Queues"


def test_nothing_relevant(setup):
    library, _fake, llm = setup
    assert ask(library, llm, "photosynthesis").found is False
