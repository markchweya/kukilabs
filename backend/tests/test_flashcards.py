import pytest

from kuki import db
from kuki.library import Library, NotFound
from kuki.llm import OllamaClient
from kuki.study.flashcards import all_cards, deck_stats, due_cards, generate_cards, review_card
from tests.fake_ollama import FakeOllama


@pytest.fixture()
def setup(settings):
    library = Library(db.connect(settings.db_path), settings)
    doc_id = library.create_document(title="DS", filename="d.md", kind="text")
    path = library.upload_path(doc_id, "d.md")
    path.write_text("# Stacks\nStack: last in, first out storage.\n\n# Queues\nQueue: first in, first out storage.")
    library.ingest_file(doc_id, path)
    fake = FakeOllama()
    return library, fake, OllamaClient(settings.ollama_host, transport=fake.transport()), doc_id


DECK = {"cards": [
    {"front": "What is a stack?", "back": "LIFO storage.", "sources": ["S1"]},
    {"front": "What is a queue?", "back": "FIFO storage.", "sources": ["S2"]},
    {"front": "Invented card", "back": "?", "sources": []},
]}


def test_generate_skips_uncited_and_duplicates(setup):
    library, fake, llm, doc_id = setup
    fake.respond("DeckDraft", DECK)
    assert [c.front for c in generate_cards(library, llm, doc_id)] == ["What is a stack?", "What is a queue?"]
    assert generate_cards(library, llm, doc_id) == []  # regenerating adds nothing new
    assert len(all_cards(library, doc_id)) == 2


def test_new_cards_are_due_and_review_reschedules(setup):
    library, fake, llm, doc_id = setup
    fake.respond("DeckDraft", DECK)
    cards = generate_cards(library, llm, doc_id)
    assert len(due_cards(library, doc_id)) == 2

    reviewed = review_card(library, cards[0].id, "good")
    assert reviewed.interval_days == 1 and reviewed.repetitions == 1
    assert [c.id for c in due_cards(library, doc_id)] == [cards[1].id]
    stats = deck_stats(library, doc_id)
    assert (stats.total, stats.due_now, stats.learned) == (2, 1, 1)
    assert library.conn.execute("SELECT grade FROM reviews").fetchone()[0] == 4


def test_offline_cards_from_definitions(setup):
    library, fake, llm, doc_id = setup
    fake.down = True
    cards = generate_cards(library, llm, doc_id)
    assert {c.front for c in cards} == {"Stack", "Queue"}


def test_review_validation(setup):
    library, *_ = setup
    with pytest.raises(ValueError):
        review_card(library, 1, "maybe")
    with pytest.raises(NotFound):
        review_card(library, 999, "good")
