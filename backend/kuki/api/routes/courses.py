"""Open Course Library endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from kuki.api.deps import get_library, get_llm
from kuki.api.routes.documents import DocumentOut
from kuki.library import Library
from kuki.llm import OllamaClient
from kuki.openlib.catalog import COURSES
from kuki.openlib.importer import ImportFailed, import_lecture

router = APIRouter(prefix="/api/courses", tags=["open courses"])


class LectureOut(BaseModel):
    number: int
    title: str
    url: str
    document_id: str | None  # set when already imported


class CourseOut(BaseModel):
    id: str
    title: str
    institution: str
    instructor: str
    subject: str
    description: str
    license: str
    license_url: str
    homepage: str
    lectures: list[LectureOut]


@router.get("", response_model=list[CourseOut])
def list_courses(library: Library = Depends(get_library)) -> list[CourseOut]:
    imported = {
        r[0]: r[1] for r in library.conn.execute("SELECT source_url, id FROM documents WHERE source_url IS NOT NULL")
    }
    return [
        CourseOut(
            id=c.id,
            title=c.title,
            institution=c.institution,
            instructor=c.instructor,
            subject=c.subject,
            description=c.description,
            license=c.license,
            license_url=c.license_url,
            homepage=c.homepage,
            lectures=[LectureOut(number=l.number, title=l.title, url=l.url, document_id=imported.get(l.url)) for l in c.lectures],
        )
        for c in COURSES
    ]


@router.post("/{course_id}/lectures/{number}/import", response_model=DocumentOut)
def import_one(
    course_id: str, number: int, library: Library = Depends(get_library), llm: OllamaClient = Depends(get_llm)
) -> DocumentOut:
    try:
        return DocumentOut.of(import_lecture(library, llm, course_id, number))
    except ImportFailed as exc:
        raise HTTPException(502 if "download" in str(exc).lower() else 422, str(exc)) from exc
