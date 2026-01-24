from __future__ import annotations

import json
import math
import re
from pathlib import Path
from typing import Dict, List, Tuple

from kuki.core.extract import extract_text_from_file

REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = REPO_ROOT / "kuki" / "data"
NOTES_DIR = DATA_DIR / "notes"
INDEX_PATH = DATA_DIR / "index.json"

DATA_DIR.mkdir(parents=True, exist_ok=True)
NOTES_DIR.mkdir(parents=True, exist_ok=True)

_WORD = re.compile(r"[A-Za-z0-9_']{2,}")

def _tokenize(text: str) -> List[str]:
    return [t.lower() for t in _WORD.findall(text or "")]

def _chunk_text(text: str, max_chars: int = 1200, overlap: int = 180) -> List[str]:
    text = (text or "").strip()
    if not text:
        return []
    chunks = []
    i = 0
    n = len(text)
    while i < n:
        end = min(n, i + max_chars)
        chunk = text[i:end].strip()
        if chunk:
            chunks.append(chunk)
        if end >= n:
            break
        i = max(0, end - overlap)
    return chunks

def _safe_filename(name: str) -> str:
    name = (name or "upload").strip()
    name = name.split("/")[-1].split("\\")[-1]
    name = re.sub(r"[^A-Za-z0-9.\-_ ()]+", "_", name)
    name = re.sub(r"\s+", " ", name).strip()
    return name or "upload"

def _load_index() -> Dict:
    if not INDEX_PATH.exists():
        return {"version": 1, "notes": [], "chunks": []}
    try:
        return json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {"version": 1, "notes": [], "chunks": []}

def _save_index(obj: Dict) -> None:
    INDEX_PATH.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")

# -----------------------------
# Public API
# -----------------------------
def ensure_index_ready() -> Dict:
    """
    Makes sure index exists and has chunks.
    Safe to call on every run.
    """
    idx = _load_index()
    chunks = idx.get("chunks", []) or []
    if not INDEX_PATH.exists() or len(chunks) == 0:
        idx = rebuild_index()
    return idx

def save_upload(uploaded_file) -> Path:
    filename = _safe_filename(getattr(uploaded_file, "name", "") or "upload")
    dest = NOTES_DIR / filename

    if dest.exists():
        stem = dest.stem
        suf = dest.suffix
        k = 2
        while True:
            cand = NOTES_DIR / f"{stem} ({k}){suf}"
            if not cand.exists():
                dest = cand
                break
            k += 1

    data = uploaded_file.getbuffer() if hasattr(uploaded_file, "getbuffer") else uploaded_file.read()
    dest.write_bytes(bytes(data))
    return dest

def list_notes() -> List[Dict]:
    out = []
    for p in sorted(NOTES_DIR.glob("*")):
        if p.is_file():
            try:
                out.append({"name": p.name, "path": str(p), "bytes": p.stat().st_size})
            except Exception:
                out.append({"name": p.name, "path": str(p), "bytes": 0})
    return out

def list_docs() -> List[Dict]:
    return list_notes()

def delete_note(filename: str) -> bool:
    p = NOTES_DIR / filename
    if not p.exists() or not p.is_file():
        return False
    try:
        p.unlink()
        return True
    except Exception:
        return False

def delete_doc(filename: str) -> bool:
    ok = delete_note(filename)
    if ok:
        rebuild_index()
    return ok

def rebuild_index() -> Dict:
    notes = list_notes()
    chunks = []

    for n in notes:
        p = Path(n["path"])
        text = extract_text_from_file(p) or ""
        for c in _chunk_text(text):
            tf: Dict[str, int] = {}
            for t in _tokenize(c):
                tf[t] = tf.get(t, 0) + 1
            chunks.append({"file": p.name, "text": c, "tf": tf})

    idx = {"version": 1, "notes": [n["name"] for n in notes], "chunks": chunks}
    _save_index(idx)
    return idx

def index_stats() -> Dict:
    idx = _load_index()
    notes = idx.get("notes", []) or []
    chunks = idx.get("chunks", []) or []
    return {
        "notes_count": len(notes),
        "chunks_count": len(chunks),
        "index_path": str(INDEX_PATH),
        "notes_dir": str(NOTES_DIR),
    }

def search_notes(query: str, top_k: int = 6) -> List[Dict]:
    q_tokens = _tokenize(query)
    if not q_tokens:
        return []

    idx = ensure_index_ready()
    chunks: List[Dict] = idx.get("chunks", []) or []
    if not chunks:
        return []

    df: Dict[str, int] = {}
    for ch in chunks:
        for t in (ch.get("tf") or {}).keys():
            df[t] = df.get(t, 0) + 1

    N = max(1, len(chunks))
    q_set = set(q_tokens)

    scored: List[Tuple[float, Dict]] = []
    for ch in chunks:
        tf = ch.get("tf") or {}
        s = 0.0
        for t in q_set:
            if t in tf:
                idf = math.log((N + 1) / (df.get(t, 0) + 1)) + 1.0
                s += float(tf[t]) * idf
        if s > 0:
            scored.append((s, ch))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [{"file": ch.get("file", ""), "text": ch.get("text", ""), "score": float(s)} for s, ch in scored[: max(1, top_k)]]
