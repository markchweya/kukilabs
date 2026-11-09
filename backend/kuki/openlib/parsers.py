"""Parsers for each course publisher's page format."""

from __future__ import annotations

import re
from dataclasses import dataclass
from urllib.parse import urljoin

from kuki.ingest.base import Segment, split_long
from kuki.ingest.plaintext import segment_text
from kuki.openlib.html_text import html_to_text


@dataclass(frozen=True)
class ParsedLecture:
    segments: list[Segment]
    audio_url: str | None = None


def parse_cs50_notes(html: str) -> ParsedLecture:
    """CS50 notes: the lecture lives in <main>, sectioned by <h2> headings."""
    text = html_to_text(html, root_tag="main")
    # Everything before the first section is the "# Lecture N" title and a
    # table of contents: neither is study content.
    first_section = text.find("\n## ")
    if first_section != -1:
        text = text[first_section + 1 :]
    return ParsedLecture(_finish(segment_text(text)))


# Yale transcripts mark chapters like: "Chapter 2. The Ring of Gyges [00:11:30]"
_CHAPTER = re.compile(r"^Chapter\s+\d+\.\s*(.+?)\s*\[(\d{1,2}:\d{2}:\d{2})\]\s*$", re.M)


def parse_oyc_transcript(html: str, page_url: str = "https://oyc.yale.edu/") -> ParsedLecture:
    """Open Yale Courses: the transcript is in #inline_content, split into timed chapters.

    Each chapter becomes a segment whose locator is its start time, so a
    citation tells the student exactly where to seek in the recording.
    """
    text = html_to_text(html, root_id="inline_content")
    text = text.replace("Back to Top", "")
    # The first two lines repeat the course and lecture titles.
    text = re.sub(r"^#{1,2} .*\n+(#{1,2} .*\n+)?", "", text)

    matches = list(_CHAPTER.finditer(text))
    if not matches:
        segments = segment_text(text)
    else:
        segments = []
        for i, m in enumerate(matches):
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            body = text[m.end():end].strip()
            if body:
                segments.append(Segment(f"{_short_time(m.group(2))} · {m.group(1)}", body))

    audio = re.search(r'href="([^"]+\.mp3)"', html)
    return ParsedLecture(_finish(segments), urljoin(page_url, audio.group(1)) if audio else None)


def _short_time(hms: str) -> str:
    """00:11:30 -> 11:30, 01:02:03 stays as is."""
    h, m, s = hms.split(":")
    return f"{int(h)}:{m}:{s}" if int(h) else f"{int(m)}:{s}"


def _finish(segments: list[Segment]) -> list[Segment]:
    return [piece for seg in segments if seg.text.strip() for piece in split_long(seg)]
