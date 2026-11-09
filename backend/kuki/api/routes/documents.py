"""Document upload, listing, inspection and deletion."""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
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
    audio_url: str | None = None
    has_local_audio: bool = False

    @classmethod
    def of(cls, doc: Document, library: Library | None = None) -> "DocumentOut":
        local = library is not None and library.local_audio_path(doc.id).exists()
        return cls(**doc.__dict__, has_local_audio=local)


class SegmentOut(BaseModel):
    id: int
    ordinal: int
    locator: str
    text: str


def nice_title(filename: str) -> str:
    """'week-4_search_algorithms (1).pptx' -> 'Week 4 search algorithms'."""
    import re

    stem = re.sub(r"\s*\(\d+\)$", "", Path(filename).stem)  # drop "(1)" download suffixes
    words = re.sub(r"[_\-.]+", " ", stem).split()
    text = " ".join(words) or "Untitled"
    return text[0].upper() + text[1:]


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
    doc_id = library.create_document(title=(title or nice_title(filename))[:200], filename=filename, kind=kind)
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
    return DocumentOut.of(library.get_document(doc_id), library)


@router.get("", response_model=list[DocumentOut])
def list_documents(library: Library = Depends(get_library)) -> list[DocumentOut]:
    return [DocumentOut.of(d) for d in library.list_documents()]


@router.get("/{doc_id}", response_model=DocumentOut)
def get_document(doc_id: str, library: Library = Depends(get_library)) -> DocumentOut:
    return DocumentOut.of(library.get_document(doc_id), library)


@router.get("/{doc_id}/segments", response_model=list[SegmentOut])
def get_segments(doc_id: str, library: Library = Depends(get_library)) -> list[SegmentOut]:
    return [SegmentOut(**dict(r)) for r in library.segments(doc_id)]


@router.post("/{doc_id}/audio", response_model=DocumentOut)
def save_recording(doc_id: str, library: Library = Depends(get_library)) -> DocumentOut:
    """Download an imported lecture's recording so it plays without internet."""
    from kuki.openlib.importer import ImportFailed, save_audio

    try:
        save_audio(library, doc_id)
    except ImportFailed as exc:
        raise HTTPException(502 if "download" in str(exc).lower() else 422, str(exc)) from exc
    return DocumentOut.of(library.get_document(doc_id), library)


@router.get("/{doc_id}/audio")
def play_recording(doc_id: str, library: Library = Depends(get_library)) -> FileResponse:
    """Serve the saved recording (supports seeking via HTTP range requests)."""
    library.get_document(doc_id)
    path = library.local_audio_path(doc_id)
    if not path.exists():
        raise HTTPException(404, "This recording hasn't been saved for offline use.")
    return FileResponse(path, media_type="audio/mpeg")


@router.delete("/{doc_id}", status_code=204)
def delete_document(doc_id: str, library: Library = Depends(get_library)) -> None:
    library.delete_document(doc_id)
