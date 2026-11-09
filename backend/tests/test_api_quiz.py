from tests.api_helpers import make_client, upload_notes

QUIZ = {"questions": [{
    "concept": "A*",
    "question": "How does A* decide which node to expand?",
    "ideal_answer": "It expands the node with the lowest f(n) = g(n) + h(n).",
    "key_ideas": ["lowest f(n)", "f = g + h"],
    "sources": ["S2"],
}]}

GRADE = {
    "claims": [
        {"claim": "it uses the heuristic", "status": "supported", "correction": ""},
        {"claim": "it only uses the heuristic", "status": "contradicted", "correction": "A* also adds the path cost g(n)."},
    ],
    "missing_ideas": ["f = g + h"],
    "misconception_type": "confused_concepts",
    "nudge": "What does A* know about the path it has already travelled?",
    "explanation": "A* uses f = g + h.",
}


def test_quiz_flow_and_insights(settings):
    client, fake = make_client(settings)
    fake.respond("QuizDraft", QUIZ)
    fake.respond("GradeDraft", GRADE)
    doc = upload_notes(client)

    questions = client.post(f"/api/documents/{doc['id']}/quiz", json={"count": 3}).json()
    assert questions[0]["concept"] == "A*" and "ideal_answer" not in questions[0]
    assert client.get(f"/api/documents/{doc['id']}/quiz").json() == questions

    grade = client.post(f"/api/questions/{questions[0]['id']}/answer", json={"answer": "it only uses the heuristic"}).json()
    assert grade["misconception_type"] == "confused_concepts"
    assert grade["ideal_answer"].startswith("It expands")

    insights = client.get("/api/insights").json()
    assert insights["concepts"][0]["concept"] == "A*" and insights["concepts"][0]["status"] == "weak"
    assert insights["mistake_patterns"] == {"confused_concepts": 1}


def test_answer_validation(settings):
    client, _ = make_client(settings)
    assert client.post("/api/questions/1/answer", json={"answer": ""}).status_code == 422
    assert client.post("/api/questions/999/answer", json={"answer": "x"}).status_code == 404
    assert client.post("/api/documents/nope/quiz").status_code == 404
