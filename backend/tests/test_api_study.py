from tests.api_helpers import make_client, upload_notes

DRAFT = {
    "concepts": [{"term": "Heuristic", "explanation": "Estimated cost to goal.", "sources": ["S2"]}],
    "key_points": [{"point": "BFS uses a queue.", "sources": ["S1"]}],
    "examples": [],
    "common_mistakes": [{"mistake": "A* ignores path cost", "correction": "f = g + h", "sources": ["S2"]}],
}


def test_generate_get_and_export_pack(settings):
    client, fake = make_client(settings)
    fake.respond("StudyPackDraft", DRAFT)
    fake.respond("PackSummaryDraft", {"title": "Search Algorithms", "overview": "How agents search."})
    doc = upload_notes(client)

    assert client.get(f"/api/documents/{doc['id']}/pack").status_code == 404
    pack = client.post(f"/api/documents/{doc['id']}/pack", json={"knowledge": "notes_only"}).json()
    assert pack["mode"] == "ai" and pack["concepts"][0]["grounded"] is True
    assert client.get(f"/api/documents/{doc['id']}/pack").json() == pack

    md = client.get(f"/api/documents/{doc['id']}/pack/markdown")
    assert md.headers["content-disposition"].endswith('search-algorithms.md"')
    assert "**Heuristic**: Estimated cost to goal. — week4, Section: Informed search" in md.text


def test_pack_requires_ready_document(settings):
    client, _ = make_client(settings)
    doc = upload_notes(client, "empty.txt", b" ")
    res = client.post(f"/api/documents/{doc['id']}/pack")
    assert res.status_code == 422 and "No readable text" in res.json()["detail"]
