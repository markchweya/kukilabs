"""SQLite storage.

One file, no server, nothing to install: the right fit for a single-user app
that runs on a laptop. Schema changes are applied as an ordered list of
migrations tracked with SQLite's built-in `user_version` pragma.
"""

from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

# Append new migrations to the end; never edit one that has shipped.
MIGRATIONS: list[str] = [
    # 1: documents and their searchable segments
    """
    CREATE TABLE documents (
        id            TEXT PRIMARY KEY,
        title         TEXT NOT NULL,
        filename      TEXT NOT NULL,
        kind          TEXT NOT NULL,              -- pdf, slides, doc, text, image, audio, web
        status        TEXT NOT NULL DEFAULT 'processing',  -- processing, ready, failed
        error         TEXT,
        source_url    TEXT,                       -- set for open-course imports
        license       TEXT,
        attribution   TEXT,
        created_at    TEXT NOT NULL DEFAULT (datetime('now'))
    );
    CREATE TABLE segments (
        id            INTEGER PRIMARY KEY,
        document_id   TEXT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
        ordinal       INTEGER NOT NULL,           -- reading order within the document
        locator       TEXT NOT NULL,              -- human label: "Slide 4", "Page 12", "12:30"
        text          TEXT NOT NULL,
        embedding     BLOB                        -- float32 vector, NULL if not embedded
    );
    CREATE INDEX segments_by_document ON segments(document_id, ordinal);
    """,
    # 2: generated study packs (stored as JSON; regenerating replaces them)
    """
    CREATE TABLE study_packs (
        document_id   TEXT PRIMARY KEY REFERENCES documents(id) ON DELETE CASCADE,
        payload       TEXT NOT NULL,
        created_at    TEXT NOT NULL DEFAULT (datetime('now'))
    );
    """,
    # 3: quiz questions and the student's attempts at them
    """
    CREATE TABLE questions (
        id            INTEGER PRIMARY KEY,
        document_id   TEXT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
        concept       TEXT NOT NULL,
        prompt        TEXT NOT NULL,
        ideal_answer  TEXT NOT NULL,
        key_ideas     TEXT NOT NULL,             -- JSON list of strings
        citations     TEXT NOT NULL,             -- JSON list of Citation
        created_at    TEXT NOT NULL DEFAULT (datetime('now'))
    );
    CREATE TABLE attempts (
        id                 INTEGER PRIMARY KEY,
        question_id        INTEGER NOT NULL REFERENCES questions(id) ON DELETE CASCADE,
        answer             TEXT NOT NULL,
        verdict            TEXT NOT NULL,        -- correct, partial, incorrect
        score              INTEGER NOT NULL,     -- 0-100
        misconception      TEXT,
        misconception_type TEXT,
        feedback           TEXT NOT NULL,        -- JSON of the full grade
        created_at         TEXT NOT NULL DEFAULT (datetime('now'))
    );
    CREATE INDEX attempts_by_question ON attempts(question_id, created_at);
    """,
]


def connect(path: Path) -> sqlite3.Connection:
    """Open a connection with sane defaults and bring the schema up to date."""
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    # WAL lets the UI read while a long ingest is writing.
    conn.execute("PRAGMA journal_mode = WAL")
    migrate(conn)
    return conn


def migrate(conn: sqlite3.Connection) -> None:
    current = conn.execute("PRAGMA user_version").fetchone()[0]
    for version, script in enumerate(MIGRATIONS[current:], start=current + 1):
        with conn:
            conn.executescript(script)
            conn.execute(f"PRAGMA user_version = {version}")


@contextmanager
def transaction(conn: sqlite3.Connection) -> Iterator[sqlite3.Connection]:
    """Commit on success, roll back on any exception."""
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
