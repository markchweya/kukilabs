import pytest

from kuki import db
from kuki.library import Library, NotFound
from kuki.llm import OllamaClient
from kuki.study.quiz import generate_quiz, grade_answer, keyword_grade, list_questions, spread_sample
from kuki.search.hybrid import Passage
from tests.fake_ollama import FakeOllama

NOTES = """# BFS
Heuristic: an estimate of cost to the goal.
BFS explores level by level using a FIFO queue, so it finds the shallowest goal first.

# DFS
DFS goes deep first using a stack. It uses little memory but may not find the shortest path.
"""


@pytest.fixture()
def setup(settings):
    library = Library(db.connect(settings.db_path), settings)
    doc_id = library.create_document(title="Search", filename="s.md", kind="text")
    path = library.upload_path(doc_id, "s.md")
    path.write_text(NOTES)
    library.ingest_file(doc_id, path)
    fake = FakeOllama()
    return library, fake, OllamaClient(settings.ollama_host, transport=fake.transport()), doc_id


QUIZ = {
    "questions": [
        {
            "concept": "BFS vs DFS",
            "question": "Why does BFS find the shallowest goal but DFS might not?",
            "ideal_answer": "BFS uses a FIFO queue and expands level by level. DFS uses a stack and dives deep.",
            "key_ideas": ["BFS uses a FIFO queue", "DFS uses a stack and goes deep first"],
            "sources": ["S1", "S2"],
        },
        {"concept": "Made up", "question": "?", "ideal_answer": "x", "key_ideas": ["x"], "sources": ["S9"]},
    ]
}


def test_generate_drops_uncited_questions_and_hides_answers(setup):
    library, fake, llm, doc_id = setup
    fake.respond("QuizDraft", QUIZ)
    questions = generate_quiz(library, llm, doc_id, count=5)
    assert [q.concept for q in questions] == ["BFS vs DFS"]
    assert "ideal_answer" not in questions[0].model_dump()
    assert list_questions(library, doc_id)[0].id == questions[0].id


def test_ai_grade_records_misconception(setup):
    library, fake, llm, doc_id = setup
    fake.respond("QuizDraft", QUIZ)
    q = generate_quiz(library, llm, doc_id)[0]
    fake.respond("GradeDraft", {
        "verdict": "partial", "score": 50, "got_right": ["BFS uses a queue"],
        "misconception": "You said DFS also uses a queue; it uses a stack.",
        "misconception_type": "confused_concepts",
        "nudge": "What data structure lets you go back to the most recent node?",
        "explanation": "DFS uses a stack.",
    })
    grade = grade_answer(library, llm, q.id, "BFS uses a queue and DFS uses a queue too")
    assert grade.mode == "ai" and grade.misconception_type == "confused_concepts"
    assert grade.ideal_answer.startswith("BFS uses")
    # The grader saw the cited lecture text, not just the model answer.
    _, body = fake.requests[-1]
    assert "FIFO queue" in body["messages"][-1]["content"]
    stored = library.conn.execute("SELECT verdict, misconception_type FROM attempts").fetchone()
    assert tuple(stored) == ("partial", "confused_concepts")


def test_offline_quiz_and_grade(setup):
    library, fake, llm, doc_id = setup
    fake.down = True
    questions = generate_quiz(library, llm, doc_id)
    assert questions and questions[0].concept == "Heuristic"
    grade = grade_answer(library, llm, questions[0].id, "an estimate of the cost to reach the goal")
    assert grade.mode == "keyword" and grade.verdict == "correct"


def test_grade_validation(setup):
    library, _fake, llm, _doc = setup
    with pytest.raises(NotFound):
        grade_answer(library, llm, 999, "x")


def test_keyword_grade_flags_missing_ideas():
    g = keyword_grade("BFS uses a queue", ["BFS uses a FIFO queue", "DFS uses a stack"], "ideal")
    assert g.verdict == "partial" and g.score == 50
    assert "DFS uses a stack" in g.misconception
    assert g.misconception_type == "missing_step"


def test_spread_sample_covers_whole_document():
    ps = [Passage(i, "d", "T", f"S{i}", "x" * 100) for i in range(50)]
    picked = spread_sample(ps, max_chars=1000, seed=1)
    ids = [p.segment_id for p in picked]
    assert len(ids) == 10 and ids == sorted(ids)
    assert max(ids) > 25  # not just the first slides


def test_short_concept_labels():
    from kuki.study.quiz import short_concept

    assert short_concept("Explaining the difference between Breadth-First Search (BFS) and Depth-First Search (DFS)") == "Difference between Breadth-First Search (BFS)"
    assert short_concept("Explaining the concept of admissible heuristics in A* search") == "Admissible heuristics in A* search"
    assert short_concept("BFS vs DFS") == "BFS vs DFS"
    assert short_concept("  ") == "General"
