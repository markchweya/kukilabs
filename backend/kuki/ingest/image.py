"""Photo/scan reader using local OCR (RapidOCR on ONNX Runtime).

OCR is optional. If the package is missing, we raise MissingDependency with
install instructions instead of failing obscurely.
"""

from __future__ import annotations

from functools import lru_cache
from importlib.util import find_spec
from pathlib import Path

from kuki.ingest.base import ExtractionError, MissingDependency, Segment, clean_text

# Ignore OCR detections the engine itself is unsure about; on handwriting these
# are mostly smudges and ruled lines.
MIN_CONFIDENCE = 0.5


def ocr_available() -> bool:
    return find_spec("rapidocr_onnxruntime") is not None


@lru_cache(maxsize=1)
def _engine():
    # Loading the ONNX models takes ~1s, so do it once per process.
    from rapidocr_onnxruntime import RapidOCR

    return RapidOCR()


def read_image(path: Path) -> list[Segment]:
    if not ocr_available():
        raise MissingDependency(
            "Reading photos needs local OCR. Install it with: pip install rapidocr-onnxruntime"
        )
    try:
        result, _elapsed = _engine()(str(path))
    except Exception as exc:  # the engine raises bare exceptions on bad images
        raise ExtractionError("Could not read text from this image.") from exc

    lines = _reading_order(result or [])
    text = clean_text("\n".join(lines))
    return [Segment("Photo", text)] if text else []


def _reading_order(detections: list) -> list[str]:
    """Sort OCR boxes top-to-bottom, then left-to-right within a line.

    Each detection is [box, text, confidence] where box is four (x, y) corners.
    Boxes whose vertical centres are within half a line height are treated as
    the same line.
    """
    items = []
    for box, text, confidence in detections:
        if float(confidence) < MIN_CONFIDENCE or not str(text).strip():
            continue
        ys = [p[1] for p in box]
        xs = [p[0] for p in box]
        items.append((sum(ys) / 4, min(xs), max(ys) - min(ys), str(text).strip()))
    items.sort()

    lines: list[list[tuple]] = []
    for item in items:
        if lines and abs(item[0] - lines[-1][0][0]) < max(item[2], 1) / 2:
            lines[-1].append(item)
        else:
            lines.append([item])
    return [" ".join(i[3] for i in sorted(line, key=lambda i: i[1])) for line in lines]
