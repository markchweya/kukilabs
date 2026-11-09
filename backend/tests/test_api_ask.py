from tests.api_helpers import make_client, upload_notes


def test_ask_and_search(settings):
    client, fake = make_client(settings)
    fake.respond("AnswerDraft", {"found": True, "answer": "A FIFO queue.", "sources": ["S1"]})
    upload_notes(client)

    ans = client.post("/api/ask", json={"question": "what does BFS use?"}).json()
    assert ans["found"] and ans["citations"][0]["locator"] == "Section: Uninformed search"

    hits = client.get("/api/search", params={"q": "heuristic"}).json()
    assert hits[0]["locator"] == "Section: Informed search"
    assert client.post("/api/ask", json={"question": ""}).status_code == 422
