from tests.api_helpers import make_client, upload_notes

DECK = {"cards": [
    {"front": "What does BFS use?", "back": "A FIFO queue.", "sources": ["S1"]},
    {"front": "Define heuristic", "back": "Estimated cost to the goal.", "sources": ["S2"]},
]}


def test_flashcard_flow(settings):
    client, fake = make_client(settings)
    fake.respond("DeckDraft", DECK)
    doc = upload_notes(client)

    cards = client.post(f"/api/documents/{doc['id']}/flashcards", json={"count": 5}).json()
    assert len(cards) == 2 and cards[0]["citations"][0]["locator"] == "Section: Uninformed search"
    assert len(client.get("/api/flashcards/due").json()) == 2

    reviewed = client.post(f"/api/flashcards/{cards[0]['id']}/review", json={"button": "easy"}).json()
    assert reviewed["repetitions"] == 1
    assert client.get("/api/flashcards/stats").json() == {"total": 2, "due_now": 1, "learned": 1}

    assert client.post(f"/api/flashcards/{cards[1]['id']}/review", json={"button": "meh"}).status_code == 422
    assert client.delete(f"/api/flashcards/{cards[1]['id']}").status_code == 204
    assert len(client.get(f"/api/documents/{doc['id']}/flashcards").json()) == 1
