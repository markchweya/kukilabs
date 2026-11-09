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
