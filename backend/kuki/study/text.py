"""Clean up short strings written by a small model.

Real Llama 3.2 3B output occasionally carries JSON-escaping debris, e.g. the
term `A"* ` (a stray quote and trailing space) instead of `A*`.
"""

from __future__ import annotations

import re

# Only double quotes: single quotes double as apostrophes ("we'll", "it’s"),
# so treating them as quotes stripped them out of real model output.
_PAIRS = {'"': '"', "“": "”"}


def clean(text: str) -> str:
    text = " ".join(str(text).split())
    # Remove quote characters that have no partner in the string.
    for open_q, close_q in _PAIRS.items():
        if open_q == close_q:
            if text.count(open_q) % 2:
                text = text.replace(open_q, "")
        elif text.count(open_q) != text.count(close_q):
            text = text.replace(open_q, "").replace(close_q, "")
    # Strip wrapping quotes around the whole string.
    if len(text) >= 2 and _PAIRS.get(text[0]) == text[-1]:
        text = text[1:-1]
    return re.sub(r"\s+([.,;:!?])", r"\1", text).strip()


# "(Source: [S7] and [S8])", "[S3]", "(S1, S2)": source tags meant for us, not the student.
_SOURCE_TAGS = re.compile(r"\s*\((?:sources?:\s*)?(?:\[?S\d+\]?(?:\s*(?:,|and|&)\s*)?)+\)|\s*\[S\d+\]", re.I)


def strip_source_tags(text: str) -> str:
    """Remove internal source tags a model copied into student-facing text."""
    return clean(_SOURCE_TAGS.sub("", text))
