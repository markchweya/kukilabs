"""Study pack generation.

Long documents do not fit in a small model's context, so we work map-style:
each batch of passages produces a partial pack with its own citations, and the
parts are merged in code (never by the model), so no citation can be lost or
rewritten during merging. One last short call writes the title and overview.
"""

from __future__ import annotations

import json
import logging
from typing import Literal

from kuki.config import Settings
from kuki.db import transaction
from kuki.library import Library, NotFound
from kuki.llm import OllamaClient, OllamaError
from kuki.search.hybrid import Passage
from kuki.study import prompts
from kuki.study.extractive import extractive_concepts, extractive_examples, extractive_points
from kuki.study.pack_models import (
    Concept,
    Example,
    KeyPoint,
    Mistake,
    PackSummaryDraft,
    StudyPack,
    StudyPackDraft,
)
from kuki.study.sources import SourceSet, batch_by_size

log = logging.getLogger(__name__)

Knowledge = Literal["notes_only", "fill_gaps"]

# Rough characters-per-token for English lecture text.
CHARS_PER_TOKEN = 3.5
# Tokens held back for the instructions and the model's answer.
RESERVED_TOKENS = 2500
MAX_ITEMS = {"concepts": 12, "key_points": 12, "examples": 5, "common_mistakes": 6}


def source_budget(settings: Settings) -> int:
    """How many characters of source text fit in one prompt."""
    return int(max(2000, (settings.num_ctx - RESERVED_TOKENS) * CHARS_PER_TOKEN))


def generate_pack(
    library: Library, llm: OllamaClient, doc_id: str, knowledge: Knowledge = "notes_only"
) -> StudyPack:
    doc = library.get_document(doc_id)
    passages = library.passages([doc_id])
    if not passages:
        raise NotFound("This document has no readable text yet.")

    try:
        pack = _ai_pack(library.settings, llm, doc.id, doc.title, passages, knowledge)
    except OllamaError as exc:
        log.info("AI pack failed (%s); building extractive pack instead.", exc)
        pack = extractive_pack(doc.id, doc.title, passages, knowledge)
        pack.notice = f"Kuki's AI is offline, so this pack was copied straight from your notes. ({exc})"

    save_pack(library, pack)
    return pack
