from __future__ import annotations
from pathlib import Path

def extract_text_from_file(path: Path) -> str:
    ext = path.suffix.lower()

    if ext == ".txt":
        return path.read_text(encoding="utf-8", errors="ignore")

    if ext == ".pdf":
        try:
            from pypdf import PdfReader
        except Exception:
            return ""
        reader = PdfReader(str(path))
        chunks = []
        for page in reader.pages:
            try:
                t = page.extract_text() or ""
            except Exception:
                t = ""
            if t.strip():
                chunks.append(t)
        return "\n".join(chunks)

    if ext == ".docx":
        try:
            from docx import Document
        except Exception:
            return ""
        doc = Document(str(path))
        return "\n".join([p.text for p in doc.paragraphs if p.text and p.text.strip()])

    if ext == ".pptx":
        try:
            from pptx import Presentation
        except Exception:
            return ""
        prs = Presentation(str(path))
        out = []
        for slide in prs.slides:
            for shape in slide.shapes:
                if hasattr(shape, "text"):
                    t = (shape.text or "").strip()
                    if t:
                        out.append(t)
        return "\n".join(out)

    return ""
