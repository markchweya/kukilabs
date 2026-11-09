"""The student's library: documents, their segments, and search over them.

This is the only module that reads and writes documents/segments, so the API
layer and the study features never touch SQL for them directly.
"""

from __future__ import annotations

import sqlite3
import uuid
from dataclasses import dataclass
from pathlib import Path

from kuki.config import Settings
from kuki.db import transaction
from kuki.ingest import ExtractionError, Segment, extract


@dataclass(frozen=True)
class Document:
    id: str
    title: str
    filename: str
    kind: str
    status: str
    error: str | None
    source_url: str | None
    license: str | None
    attribution: str | None
    created_at: str
    segment_count: int


class NotFound(LookupError):
    pass


_DOC_COLUMNS = """
    d.id, d.title, d.filename, d.kind, d.status, d.error, d.source_url, d.license,
    d.attribution, d.created_at,
    (SELECT COUNT(*) FROM segments s WHERE s.document_id = d.id) AS segment_count
"""


class Library:
    def __init__(self, conn: sqlite3.Connection, settings: Settings):
        self.conn = conn
        self.settings = settings

    # ---- documents -------------------------------------------------------

    def create_document(
        self,
        *,
        title: str,
        filename: str,
        kind: str,
        source_url: str | None = None,
        license: str | None = None,
        attribution: str | None = None,
    ) -> str:
        doc_id = uuid.uuid4().hex[:12]
        with transaction(self.conn):
            self.conn.execute(
                "INSERT INTO documents(id, title, filename, kind, source_url, license, attribution)"
                " VALUES (?, ?, ?, ?, ?, ?, ?)",
                (doc_id, title, filename, kind, source_url, license, attribution),
            )
        return doc_id

    def list_documents(self) -> list[Document]:
        rows = self.conn.execute(f"SELECT {_DOC_COLUMNS} FROM documents d ORDER BY d.created_at DESC, d.rowid DESC")
        return [Document(**dict(r)) for r in rows]

    def get_document(self, doc_id: str) -> Document:
        row = self.conn.execute(f"SELECT {_DOC_COLUMNS} FROM documents d WHERE d.id = ?", (doc_id,)).fetchone()
        if row is None:
            raise NotFound(f"No document with id {doc_id}")
        return Document(**dict(row))

    def delete_document(self, doc_id: str) -> None:
        self.get_document(doc_id)  # raises NotFound
        with transaction(self.conn):
            self.conn.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
        # Remove the stored upload too: deleting means deleting.
        for path in self.settings.uploads_dir.glob(f"{doc_id}.*"):
            path.unlink(missing_ok=True)

    def upload_path(self, doc_id: str, filename: str) -> Path:
        """Where an upload is stored: <data>/uploads/<id><ext>."""
        return self.settings.uploads_dir / f"{doc_id}{Path(filename).suffix.lower()}"

    # ---- ingestion -------------------------------------------------------

    def ingest_file(self, doc_id: str, path: Path) -> None:
        """Read a stored upload and save its segments.

        Never raises for a bad file: the failure is recorded on the document
        so the UI can show the student what went wrong.
        """
        try:
            segments = extract(path)
        except ExtractionError as exc:
            self._fail(doc_id, str(exc))
            return
        except Exception as exc:  # a reader bug must not leave a doc stuck "processing"
            self._fail(doc_id, f"Unexpected error while reading the file: {exc}")
            return
        self.save_segments(doc_id, segments)

    def save_segments(self, doc_id: str, segments: list[Segment]) -> None:
        """Replace a document's segments and mark it ready."""
        with transaction(self.conn):
            self.conn.execute("DELETE FROM segments WHERE document_id = ?", (doc_id,))
            self.conn.executemany(
                "INSERT INTO segments(document_id, ordinal, locator, text) VALUES (?, ?, ?, ?)",
                [(doc_id, i, s.locator, s.text) for i, s in enumerate(segments)],
            )
            self.conn.execute("UPDATE documents SET status = 'ready', error = NULL WHERE id = ?", (doc_id,))

    def _fail(self, doc_id: str, message: str) -> None:
        with transaction(self.conn):
            self.conn.execute("UPDATE documents SET status = 'failed', error = ? WHERE id = ?", (message, doc_id))

    def segments(self, doc_id: str) -> list[sqlite3.Row]:
        self.get_document(doc_id)
        return self.conn.execute(
            "SELECT id, ordinal, locator, text FROM segments WHERE document_id = ? ORDER BY ordinal", (doc_id,)
        ).fetchall()
