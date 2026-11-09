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
        "checks": [
            {"status": "supported", "correction": ""},
            {"status": "contradicted", "correction": "DFS uses a stack."},
        ],
        "missing_ideas": ["DFS uses a stack and goes deep first"],
        "misconception_type": "confused_concepts",
        "nudge": "What data structure lets you go back to the most recent node?",
        "explanation": "DFS uses a stack.",
    })
    grade = grade_answer(library, llm, q.id, "BFS uses a FIFO queue. DFS uses a queue too.")
    assert grade.mode == "ai" and grade.misconception_type == "confused_concepts"
    assert grade.misconception == "You said “DFS uses a queue too”, but DFS uses a stack."
    assert grade.got_right == ["BFS uses a FIFO queue"]
    assert (grade.verdict, grade.score) == ("partial", 20)  # 50% coverage - 30 for the contradiction
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


# ---- regression cases from a real Llama 3.2 3B run --------------------------

from kuki.study.quiz import aggregate_grade, split_claims, tidy_correction  # noqa: E402
from kuki.study.quiz_models import GradeDraft  # noqa: E402

KEY_IDEAS = ["BFS uses a FIFO queue", "DFS uses a stack and goes deep first"]


def draft(checks, missing=(), kind="none"):
    return GradeDraft(
        checks=[{"status": s, "correction": corr} for s, corr in checks],
        missing_ideas=list(missing), misconception_type=kind, nudge="Think about it?", explanation="E.",
    )


def test_split_claims():
    assert split_claims("BFS uses a FIFO queue; DFS uses a stack. Yes.") == ["BFS uses a FIFO queue", "DFS uses a stack, yes"]
    assert split_claims("BFS and DFS both explore a graph.") == ["BFS and DFS both explore a graph"]  # no split on "and"
    assert split_claims("   ") == []


def test_contradiction_is_named_with_the_correction():
    claims = split_claims("DFS finds the shortest path because it uses a queue.")
    result = aggregate_grade(draft([("contradicted", "DFS uses a stack, not a queue.")], missing=KEY_IDEAS, kind="confused_concepts"), claims, KEY_IDEAS)
    assert (result.verdict, result.score, result.misconception_type) == ("incorrect", 0, "confused_concepts")
    assert result.misconception == "You said “DFS finds the shortest path because it uses a queue”, but DFS uses a stack, not a queue."
    assert result.got_right == []


def test_correct_answer_gets_no_misconception():
    # The first real-model grader marked this answer "partial" with a false misconception.
    claims = split_claims("BFS uses a FIFO queue. DFS uses a stack and goes deep first.")
    result = aggregate_grade(draft([("supported", ""), ("supported", "None")], kind="overgeneralization"), claims, KEY_IDEAS)
    assert (result.verdict, result.score, result.misconception, result.misconception_type) == ("correct", 100, "", "none")
    assert result.got_right == claims and result.nudge == ""


def test_ideas_stated_in_the_answer_are_never_missing():
    # The real model listed "BFS uses a FIFO queue" as missing from an answer that said it.
    claims = split_claims("BFS uses a FIFO queue so it explores level by level.")
    result = aggregate_grade(draft([("supported", "")], missing=["BFS uses a FIFO queue", KEY_IDEAS[1], "invented idea"]), claims, KEY_IDEAS)
    assert result.misconception == "Your answer leaves out: DFS uses a stack and goes deep first"
    assert (result.verdict, result.score, result.misconception_type) == ("partial", 50, "missing_step")


def test_fewer_checks_than_claims_and_empty_answers():
    claims = ["BFS uses a FIFO queue", "something else entirely"]
    assert aggregate_grade(draft([("supported", "")]), claims, KEY_IDEAS).got_right == ["BFS uses a FIFO queue"]
    result = aggregate_grade(draft([], missing=KEY_IDEAS, kind="off_topic"), [], KEY_IDEAS)
    assert (result.verdict, result.score) == ("incorrect", 0)


def test_tidy_correction():
    assert tidy_correction("None") == ""
    assert tidy_correction("A. B. C. (Lecture Source: Slide 4)") == "A. B."


def test_grade_schema_is_sized_to_the_answer(setup):
    library, fake, llm, doc_id = setup
    fake.respond("QuizDraft", QUIZ)
    q = generate_quiz(library, llm, doc_id)[0]
    fake.respond("GradeDraft", {"checks": [{"status": "supported", "correction": ""}] * 2, "missing_ideas": [],
                                "misconception_type": "none", "nudge": "", "explanation": "E."})
    grade_answer(library, llm, q.id, "BFS uses a FIFO queue. DFS uses a stack and goes deep first.")
    _, body = fake.requests[-1]
    checks = body["format"]["properties"]["checks"]
    assert (checks["minItems"], checks["maxItems"]) == (2, 2)
    assert body["format"]["properties"]["missing_ideas"]["maxItems"] == 2
    assert body["options"]["num_predict"] == 700
