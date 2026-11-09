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


def test_ai_grade_records_misconception(setup, monkeypatch):
    from kuki.study import quiz

    # The fake's letter-count embeddings make everything look alike; pin similarity.
    monkeypatch.setattr(quiz, "_best_similarity", lambda lib, llm, ideas, claims: {i: 0.0 for i in ideas})
    library, fake, llm, doc_id = setup
    fake.respond("QuizDraft", QUIZ)
    q = generate_quiz(library, llm, doc_id)[0]
    fake.respond("GradeDraft", {
        "checks": [
            {"status": "supported", "correction": ""},
            {"status": "contradicted", "correction": "DFS uses a stack."},
        ],
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


def draft(checks, kind="none"):
    return GradeDraft(
        checks=[{"status": s, "correction": corr} for s, corr in checks],
        misconception_type=kind, nudge="Think about it?", explanation="E.",
    )


def test_split_claims():
    assert split_claims("BFS uses a FIFO queue; DFS uses a stack. Yes.") == ["BFS uses a FIFO queue", "DFS uses a stack, yes"]
    assert split_claims("BFS and DFS explore a graph.") == ["BFS and DFS explore a graph"]  # no split on plain "and"
    assert split_claims("   ") == []
    # Half-right compound claims are judged one half at a time.
    assert split_claims("BFS and DFS both use a queue.") == ["BFS use a queue", "DFS use a queue"]
    assert split_claims("Greedy search and A* each use a heuristic") == ["Greedy search use a heuristic", "A* use a heuristic"]


def test_contradiction_is_named_with_the_correction():
    claims = split_claims("DFS finds the shortest path because it uses a queue.")
    result = aggregate_grade(draft([("contradicted", "DFS uses a stack, not a queue.")], kind="confused_concepts"), claims, KEY_IDEAS, KEY_IDEAS)
    assert (result.verdict, result.score, result.misconception_type) == ("incorrect", 0, "confused_concepts")
    assert result.misconception == "You said “DFS finds the shortest path because it uses a queue”, but DFS uses a stack, not a queue."
    assert result.got_right == []


def test_correct_answer_gets_no_misconception():
    # The first real-model grader marked this answer "partial" with a false misconception.
    claims = split_claims("BFS uses a FIFO queue. DFS uses a stack and goes deep first.")
    result = aggregate_grade(draft([("supported", ""), ("supported", "None")], kind="overgeneralization"), claims, KEY_IDEAS, [])
    assert (result.verdict, result.score, result.misconception, result.misconception_type) == ("correct", 100, "", "none")
    assert result.got_right == claims and result.nudge == ""


def test_missing_idea_without_errors_is_a_missing_step():
    claims = split_claims("BFS uses a FIFO queue so it explores level by level.")
    result = aggregate_grade(draft([("supported", "")]), claims, KEY_IDEAS, [KEY_IDEAS[1], "invented idea"])
    assert result.misconception == "Your answer leaves out: DFS uses a stack and goes deep first"
    assert (result.verdict, result.score, result.misconception_type) == ("partial", 50, "missing_step")


def test_fewer_checks_than_claims_and_empty_answers():
    claims = ["BFS uses a FIFO queue", "something else entirely"]
    assert aggregate_grade(draft([("supported", "")]), claims, KEY_IDEAS, []).got_right == ["BFS uses a FIFO queue"]
    result = aggregate_grade(draft([], kind="off_topic"), [], KEY_IDEAS, KEY_IDEAS)
    assert (result.verdict, result.score) == ("incorrect", 0)


def test_tidy_correction():
    assert tidy_correction("None") == ""
    assert tidy_correction("A. B. C. (Lecture Source: Slide 4)") == "A. B."


def test_grade_schema_is_sized_to_the_answer(setup):
    library, fake, llm, doc_id = setup
    fake.respond("QuizDraft", QUIZ)
    q = generate_quiz(library, llm, doc_id)[0]
    fake.respond("GradeDraft", {"checks": [{"status": "supported", "correction": ""}] * 2,
                                "misconception_type": "none", "nudge": "", "explanation": "E."})
    grade_answer(library, llm, q.id, "BFS uses a FIFO queue. DFS uses a stack and goes deep first.")
    body = next(b for path, b in fake.requests if path == "/api/chat" and b["format"]["title"] == "GradeDraft")
    checks = body["format"]["properties"]["checks"]
    assert (checks["minItems"], checks["maxItems"]) == (2, 2)
    assert "missing_ideas" not in body["format"]["properties"]
    assert body["options"]["num_predict"] == 700


def test_unconfirmed_contradiction_is_not_reported(setup):
    # Real failure: "BFS uses a queue, not a FIFO queue" told to a correct student.
    library, fake, llm, doc_id = setup
    fake.respond("QuizDraft", QUIZ)
    q = generate_quiz(library, llm, doc_id)[0]
    fake.respond("GradeDraft", {
        "checks": [{"status": "contradicted", "correction": "BFS uses a queue, not a FIFO queue."},
                   {"status": "supported", "correction": ""}], "misconception_type": "confused_concepts", "nudge": "Hmm?", "explanation": "E.",
    })
    fake.respond("AgreementCheck", {"lecture_quote": "BFS explores level by level using a FIFO queue.", "agrees": True})
    grade = grade_answer(library, llm, q.id, "BFS uses a FIFO queue. DFS uses a stack and goes deep first.")
    assert grade.misconception == "" and grade.verdict == "correct"
    assert grade.got_right == ["BFS uses a FIFO queue", "DFS uses a stack and goes deep first"]


def test_confirmed_contradiction_is_reported(setup):
    library, fake, llm, doc_id = setup
    fake.respond("QuizDraft", QUIZ)
    q = generate_quiz(library, llm, doc_id)[0]
    fake.respond("GradeDraft", {
        "checks": [{"status": "contradicted", "correction": "DFS uses a stack."}], "misconception_type": "confused_concepts", "nudge": "Hmm?", "explanation": "E.",
    })
    fake.respond("AgreementCheck", {"lecture_quote": "DFS goes deep first using a stack.", "agrees": False})
    grade = grade_answer(library, llm, q.id, "DFS uses a queue.")
    assert grade.misconception.startswith("You said “DFS uses a queue”")


def test_nothing_right_caps_the_score():
    # Real run: an answer with no correct claim scored 75 because the model
    # reported only one missing idea.
    result = aggregate_grade(draft([("not_in_notes", ""), ("not_in_notes", "")]), ["a b c", "d e f"], KEY_IDEAS, [KEY_IDEAS[0]])
    assert (result.verdict, result.score) == ("incorrect", 30)


def test_every_claim_is_rechecked(setup):
    # Real failure: the grader marked "DFS uses a queue" as supported.
    library, fake, llm, doc_id = setup
    fake.respond("QuizDraft", QUIZ)
    q = generate_quiz(library, llm, doc_id)[0]
    fake.respond("GradeDraft", {"checks": [{"status": "supported", "correction": ""}] * 2,
                                "misconception_type": "none", "nudge": "Hmm?", "explanation": "E."})
    quotes = iter([
        {"lecture_quote": "BFS explores level by level using a FIFO queue.", "agrees": False},  # words match: supported anyway
        {"lecture_quote": "DFS goes deep first using a stack.", "agrees": False},
    ])
    fake.respond("AgreementCheck", lambda _req: next(quotes))
    grade = grade_answer(library, llm, q.id, "BFS uses a FIFO queue. DFS uses a queue.")
    # "DFS uses a queue" loses its credit, but with only one signal against it
    # the student isn't told it's wrong.
    assert grade.got_right == ["BFS uses a FIFO queue"]
    assert not grade.misconception.startswith("You said")


def test_quote_support_needs_every_word():
    from kuki.study.quiz import _quote_supports

    assert _quote_supports("BFS use a queue", "BFS uses a queue: first in, first out.")
    assert not _quote_supports("DFS use a queue", "DFS uses a stack: last in, first out.")


def test_paraphrased_ideas_are_not_missing(setup, monkeypatch):
    # Real failure: "level by level" wasn't accepted for "all nodes at a given depth".
    from kuki.study import quiz

    library, fake, llm, doc_id = setup
    fake.respond("QuizDraft", QUIZ)
    q = generate_quiz(library, llm, doc_id)[0]
    fake.respond("GradeDraft", {"checks": [{"status": "supported", "correction": ""}],
                                "misconception_type": "none", "nudge": "Hmm?", "explanation": "E."})
    fake.respond("AgreementCheck", {"lecture_quote": "BFS explores level by level", "agrees": True})
    # Stand-in for embeddings: the paraphrase is close, the unrelated idea is not.
    monkeypatch.setattr(quiz, "_best_similarity", lambda lib, llm, ideas, claims: {
        "BFS uses a FIFO queue": 0.81, "DFS uses a stack and goes deep first": 0.52,
    })
    grade = grade_answer(library, llm, q.id, "BFS goes level by level with a first-in first-out structure.")
    assert grade.misconception == "Your answer leaves out: DFS uses a stack and goes deep first"


def test_wrong_claims_never_cover_ideas(setup, monkeypatch):
    # Similarity is topical: "both use a queue" is close to "DFS uses a stack".
    # Only verified-correct claims may cover an idea.
    from kuki.study import quiz

    library, *_ = setup
    calls = []
    monkeypatch.setattr(quiz, "_best_similarity", lambda lib, llm, ideas, claims: calls.append(claims) or {i: 0.9 for i in ideas})
    assert quiz._missing_ideas(library, None, "x", KEY_IDEAS, supported=[]) == KEY_IDEAS
    assert calls == []


def test_idea_check_falls_back_to_llm_without_embeddings(setup):
    library, fake, llm, doc_id = setup
    fake.models = ["llama3.2:3b"]
    from kuki.study import quiz

    def no_embed(*_a, **_k):
        raise quiz.OllamaError("model 'nomic-embed-text' not found")

    llm.embed = no_embed
    fake.respond("IdeaCheck", {"student_quote": "BFS goes level by level", "stated": True})
    missing = quiz._missing_ideas(library, llm, "BFS goes level by level.", ["BFS explores each depth in turn"], ["BFS goes level by level"])
    assert missing == []
