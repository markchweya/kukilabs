"""Lecture recording reader using local speech-to-text (faster-whisper).

The transcript is grouped into roughly one-minute windows so each segment is a
useful retrieval unit and its locator ("12:00-13:04") lets a student jump to
that moment in the recording.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from importlib.util import find_spec
from pathlib import Path

from kuki.ingest.base import ExtractionError, MissingDependency, Segment, clean_text

WINDOW_SECONDS = 60.0


@dataclass(frozen=True)
class Utterance:
    start: float
    end: float
    text: str


def whisper_available() -> bool:
    return find_spec("faster_whisper") is not None


@lru_cache(maxsize=2)
def _model(size: str):
    from faster_whisper import WhisperModel

    # int8 on CPU keeps memory low and runs on any laptop; no GPU required.
    return WhisperModel(size, device="cpu", compute_type="int8")


def read_audio(path: Path, model_size: str = "base") -> list[Segment]:
    if not whisper_available():
        raise MissingDependency(
            "Transcribing recordings needs local speech-to-text. Install it with: pip install faster-whisper"
        )
    try:
        # vad_filter skips long silences, which are common in lecture recordings.
        pieces, _info = _model(model_size).transcribe(str(path), vad_filter=True)
        utterances = [Utterance(p.start, p.end, p.text) for p in pieces]
    except Exception as exc:
        raise ExtractionError("Could not transcribe this recording.") from exc
    return group_by_window(utterances)


def group_by_window(utterances: list[Utterance], window: float = WINDOW_SECONDS) -> list[Segment]:
    """Merge consecutive utterances into ~`window`-second segments."""
    segments: list[Segment] = []
    bucket: list[Utterance] = []
    for u in utterances:
        if bucket and u.end - bucket[0].start > window:
            segments.append(_to_segment(bucket))
            bucket = []
        bucket.append(u)
    if bucket:
        segments.append(_to_segment(bucket))
    return [s for s in segments if s.text]


def _to_segment(bucket: list[Utterance]) -> Segment:
    text = clean_text(" ".join(u.text.strip() for u in bucket))
    return Segment(f"{timestamp(bucket[0].start)}-{timestamp(bucket[-1].end)}", text)


def timestamp(seconds: float) -> str:
    """Format seconds as m:ss, or h:mm:ss for long recordings."""
    total = int(seconds)
    h, rem = divmod(total, 3600)
    m, s = divmod(rem, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"
