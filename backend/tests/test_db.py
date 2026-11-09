from kuki import db


def test_migrations_create_schema_and_are_idempotent(tmp_path):
    conn = db.connect(tmp_path / "k.db")
    version = conn.execute("PRAGMA user_version").fetchone()[0]
    assert version == len(db.MIGRATIONS)
    db.migrate(conn)  # running again is a no-op
    tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    assert {"documents", "segments", "study_packs", "questions", "attempts"} <= tables


def test_deleting_document_cascades_to_segments(tmp_path):
    conn = db.connect(tmp_path / "k.db")
    with db.transaction(conn):
        conn.execute("INSERT INTO documents(id, title, filename, kind) VALUES ('d1', 'T', 'f.pdf', 'pdf')")
        conn.execute("INSERT INTO segments(document_id, ordinal, locator, text) VALUES ('d1', 0, 'Page 1', 'x')")
    with db.transaction(conn):
        conn.execute("DELETE FROM documents WHERE id = 'd1'")
    assert conn.execute("SELECT COUNT(*) FROM segments").fetchone()[0] == 0
