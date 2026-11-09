"""Fetch a catalogued lecture and add it to the student's library.

This is the only part of Kuki that touches the internet, and only when the
student clicks Import. It can be switched off with KUKI_ALLOW_DOWNLOADS=0.
"""

from __future__ import annotations

from pathlib import Path

import httpx

from kuki import __version__
from kuki.library import Document, Library
from kuki.llm import OllamaClient
from kuki.openlib.catalog import get_course
from kuki.openlib.parsers import ParsedLecture, parse_cs50_notes, parse_oyc_transcript

# Identify ourselves honestly to the publishers' servers.
USER_AGENT = f"Kuki/{__version__} (personal study app; open-course importer; +https://github.com/markchweya/kukilabs)"

PARSERS = {
    "cs50_notes": lambda html, url: parse_cs50_notes(html),
    "oyc_transcript": parse_oyc_transcript,
}


class ImportFailed(RuntimeError):
    pass


def import_lecture(
    library: Library,
    llm: OllamaClient | None,
    course_id: str,
    number: int,
    http: httpx.Client | None = None,
) -> Document:
    if not library.settings.allow_downloads:
        raise ImportFailed("Downloads are turned off (KUKI_ALLOW_DOWNLOADS=0).")
    try:
        course = get_course(course_id)
        lecture = course.lecture(number)
    except KeyError as exc:
        raise ImportFailed(str(exc)) from None

    existing = library.find_by_source(lecture.url)
    if existing is not None:
        return existing  # importing twice is a no-op, not a duplicate

    parsed = _fetch_and_parse(http, course.format, lecture.url)
    if not parsed.segments:
        raise ImportFailed("The lecture page had no readable content. The site may have changed.")

    doc_id = library.create_document(
        title=f"{lecture.title} · {course.title.split(' (')[0]}",
        filename=lecture.url,
        kind="web",
        source_url=lecture.url,
        license=course.license,
        attribution=course.attribution(lecture),
        audio_url=parsed.audio_url,
    )
    library.save_segments(doc_id, parsed.segments)
    if llm is not None:
        library.embed_missing(llm, doc_id)
    return library.get_document(doc_id)


def _fetch_and_parse(http: httpx.Client | None, fmt: str, url: str) -> ParsedLecture:
    own_client = http is None
    client = http or httpx.Client(timeout=30, follow_redirects=True)
    try:
        res = client.get(url, headers={"User-Agent": USER_AGENT})
        res.raise_for_status()
    except httpx.HTTPError as exc:
        raise ImportFailed(f"Couldn't download the lecture ({exc}). Check your internet connection.") from exc
    finally:
        if own_client:
            client.close()
    return PARSERS[fmt](res.text, url)


# Lecture recordings are ~40 MB; refuse anything absurd.
MAX_AUDIO_BYTES = 400 * 1024 * 1024


def save_audio(library: Library, doc_id: str, http: httpx.Client | None = None) -> Path:
    """Download an imported lecture's recording so it plays offline."""
    if not library.settings.allow_downloads:
        raise ImportFailed("Downloads are turned off (KUKI_ALLOW_DOWNLOADS=0).")
    doc = library.get_document(doc_id)
    if not doc.audio_url:
        raise ImportFailed("This lecture has no recording to save.")
    dest = library.local_audio_path(doc_id)
    if dest.exists():
        return dest

    partial = dest.with_suffix(".part")
    own_client = http is None
    client = http or httpx.Client(timeout=60, follow_redirects=True)
    try:
        with client.stream("GET", doc.audio_url, headers={"User-Agent": USER_AGENT}) as res:
            res.raise_for_status()
            written = 0
            with partial.open("wb") as out:
                for chunk in res.iter_bytes(1024 * 256):
                    written += len(chunk)
                    if written > MAX_AUDIO_BYTES:
                        raise ImportFailed("The recording is unexpectedly large; not saved.")
                    out.write(chunk)
        # Rename only when complete, so a cut-off download never looks finished.
        partial.replace(dest)
        return dest
    except httpx.HTTPError as exc:
        raise ImportFailed(f"Couldn't download the recording ({exc}).") from exc
    finally:
        partial.unlink(missing_ok=True)
        if own_client:
            client.close()
