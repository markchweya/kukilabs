"""Study pack endpoints."""

from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, Depends, Response
from pydantic import BaseModel

from kuki.api.deps import get_library, get_llm
from kuki.library import Library, NotFound
from kuki.llm import OllamaClient
from kuki.study.pack_models import StudyPack
from kuki.study.packs import generate_pack, load_pack

router = APIRouter(prefix="/api/documents/{doc_id}/pack", tags=["study"])


class PackRequest(BaseModel):
    knowledge: Literal["notes_only", "fill_gaps"] = "notes_only"


def _ensure_ready(library: Library, doc_id: str) -> None:
    doc = library.get_document(doc_id)
    if doc.status != "ready":
        raise ValueError("This document is still being read. Try again in a moment." if doc.status == "processing" else doc.error or "This document could not be read.")


@router.get("", response_model=StudyPack)
def get_pack(doc_id: str, library: Library = Depends(get_library)) -> StudyPack:
    library.get_document(doc_id)
    pack = load_pack(library, doc_id)
    if pack is None:
        raise NotFound("No study pack yet. Generate one first.")
    return pack


@router.post("", response_model=StudyPack)
def create_pack(
    doc_id: str,
    body: PackRequest | None = None,
    library: Library = Depends(get_library),
    llm: OllamaClient = Depends(get_llm),
) -> StudyPack:
    """Generate (or regenerate) a study pack. Can take a minute on a CPU."""
    _ensure_ready(library, doc_id)
    return generate_pack(library, llm, doc_id, (body or PackRequest()).knowledge)


@router.get("/markdown")
def export_markdown(doc_id: str, library: Library = Depends(get_library)) -> Response:
    """Download the pack as Markdown, with citations, for printing or Obsidian/Notion."""
    pack = get_pack(doc_id, library)
    return Response(
        content=pack_to_markdown(pack),
        media_type="text/markdown; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{_slug(pack.title)}.md"'},
    )


def pack_to_markdown(pack: StudyPack) -> str:
    def cite(item) -> str:
        if not item.citations:
            return " _(not from your notes)_"
        return " — " + ", ".join(f"{c.document_title}, {c.locator}" for c in item.citations)

    lines = [f"# {pack.title}", "", pack.overview, ""]
    if pack.concepts:
        lines += ["## Key concepts", ""] + [f"- **{c.term}**: {c.explanation}{cite(c)}" for c in pack.concepts] + [""]
    if pack.key_points:
        lines += ["## Main points", ""] + [f"- {p.point}{cite(p)}" for p in pack.key_points] + [""]
    if pack.examples:
        lines += ["## Examples", ""]
        for e in pack.examples:
            lines += [f"### {e.title}", "", e.explanation + cite(e), ""]
    if pack.common_mistakes:
        lines += ["## Common mistakes", ""] + [
            f"- ❌ {m.mistake}\n  ✅ {m.correction}{cite(m)}" for m in pack.common_mistakes
        ] + [""]
    lines.append(f"_Made with Kuki ({'AI: ' + pack.model if pack.model else 'extractive mode'})._")
    return "\n".join(lines)


def _slug(title: str) -> str:
    return "".join(ch if ch.isalnum() else "-" for ch in title.lower()).strip("-")[:60] or "study-pack"
