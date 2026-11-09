"""Document upload, listing, inspection and deletion."""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, UploadFile
from pydantic import BaseModel

from kuki.api.deps import get_library, get_llm, get_settings, open_library
from kuki.config import Settings
from kuki.ingest import kind_for
from kuki.library import Document, Library
from kuki.llm import OllamaClient

router = APIRouter(prefix="/api/documents", tags=["documents"])

CHUNK = 1024 * 1024


class DocumentOut(BaseModel):
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

    @classmethod
    def of(cls, doc: Document) -> "DocumentOut":
        return cls(**doc.__dict__)


class SegmentOut(BaseModel):
    id: int
    ordinal: int
    locator: str
    text: str


def process_document(settings: Settings, llm: OllamaClient, doc_id: str, path: Path) -> None:
    """Background job: read the file, then embed it if the model is available."""
    library = open_library(settings)
    try:
        library.ingest_file(doc_id, path)
        library.embed_missing(llm, doc_id)
    finally:
        library.conn.close()


@router.post("", response_model=DocumentOut, status_code=201)
def upload(
    background: BackgroundTasks,
    file: UploadFile = File(...),
    title: str | None = Form(None),
    library: Library = Depends(get_library),
    settings: Settings = Depends(get_settings),
    llm: OllamaClient = Depends(get_llm),
) -> DocumentOut:
    filename = Path(file.filename or "upload").name  # never trust client paths
    kind = kind_for(filename)  # 422 for unsupported types, before saving anything
    doc_id = library.create_document(title=(title or Path(filename).stem).strip()[:200], filename=filename, kind=kind)
    dest = library.upload_path(doc_id, filename)

    # Stream to disk in chunks so a 200 MB lecture video never sits in memory,
    # and stop as soon as the size limit is crossed.
    limit = settings.max_upload_mb * 1024 * 1024
    written = 0
    with dest.open("wb") as out:
        while chunk := file.file.read(CHUNK):
            written += len(chunk)
            if written > limit:
                out.close()
                library.delete_document(doc_id)
                raise HTTPException(413, f"File is larger than {settings.max_upload_mb} MB.")
            out.write(chunk)

    background.add_task(process_document, settings, llm, doc_id, dest)
    return DocumentOut.of(library.get_document(doc_id))


@router.get("", response_model=list[DocumentOut])
def list_documents(library: Library = Depends(get_library)) -> list[DocumentOut]:
    return [DocumentOut.of(d) for d in library.list_documents()]


@router.get("/{doc_id}", response_model=DocumentOut)
def get_document(doc_id: str, library: Library = Depends(get_library)) -> DocumentOut:
    return DocumentOut.of(library.get_document(doc_id))


@router.get("/{doc_id}/segments", response_model=list[SegmentOut])
def get_segments(doc_id: str, library: Library = Depends(get_library)) -> list[SegmentOut]:
    return [SegmentOut(**dict(r)) for r in library.segments(doc_id)]


@router.delete("/{doc_id}", status_code=204)
def delete_document(doc_id: str, library: Library = Depends(get_library)) -> None:
    library.delete_document(doc_id)
