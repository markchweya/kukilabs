import json

from kuki import db
from kuki.library import Library
from kuki.study.insights import build_insights


def test_insights_track_progress_and_patterns(settings):
    library = Library(db.connect(settings.db_path), settings)
    doc = library.create_document(title="Search", filename="s.md", kind="text")
    conn = library.conn

    def question(concept):
        return conn.execute(
            "INSERT INTO questions(document_id, concept, prompt, ideal_answer, key_ideas, citations) VALUES (?, ?, 'q', 'a', '[]', '[]')",
            (doc, concept),
        ).lastrowid

    def attempt(qid, score, kind, note=""):
        conn.execute(
            "INSERT INTO attempts(question_id, answer, verdict, score, misconception, misconception_type, feedback)"
            " VALUES (?, 'x', 'partial', ?, ?, ?, ?)",
            (qid, score, note, kind, json.dumps({})),
        )

    bfs, dfs, astar = question("BFS"), question("DFS"), question("A*")
    attempt(bfs, 30, "confused_concepts", "mixed up queue and stack")
    attempt(bfs, 60, "missing_step")
    attempt(dfs, 20, "confused_concepts", "thinks DFS is optimal")
    attempt(astar, 90, "none")
    conn.commit()

    insights = build_insights(library)
    assert insights.total_attempts == 4
    assert [(c.concept, c.status) for c in insights.concepts] == [
        ("DFS", "weak"), ("BFS", "improving"), ("A*", "mastered"),
    ]
    assert insights.concepts[0].latest_misconception == "thinks DFS is optimal"
    assert list(insights.mistake_patterns.items())[0] == ("confused_concepts", 2)
