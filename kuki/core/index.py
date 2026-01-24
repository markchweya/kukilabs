from __future__ import annotations
import json
from pathlib import Path
from typing import List, Dict, Any
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

def _chunks(text: str, chunk_size: int = 900, overlap: int = 150) -> List[str]:
    text = text.replace("\r\n", "\n").strip()
    if not text:
        return []
    chunks = []
    i = 0
    while i < len(text):
        j = min(len(text), i + chunk_size)
        chunk = text[i:j].strip()
        if chunk:
            chunks.append(chunk)
        i += max(1, chunk_size - overlap)
    return chunks

def build_or_update_index(index_dir: Path, embed_model_name: str, documents: List[Dict[str, Any]]) -> None:
    index_dir.mkdir(parents=True, exist_ok=True)
    model = SentenceTransformer(embed_model_name)

    all_chunks = []
    for d in documents:
        for c in _chunks(d.get("text","")):
            all_chunks.append({"doc_id": d["id"], "title": d.get("title",""), "text": c})

    if not all_chunks:
        (index_dir / "chunks.json").write_text("[]", encoding="utf-8")
        dim = model.get_sentence_embedding_dimension()
        faiss.write_index(faiss.IndexFlatIP(dim), str(index_dir / "index.faiss"))
        return

    texts = [c["text"] for c in all_chunks]
    emb = model.encode(texts, normalize_embeddings=True)
    emb = np.asarray(emb, dtype="float32")

    dim = emb.shape[1]
    idx = faiss.IndexFlatIP(dim)
    idx.add(emb)

    faiss.write_index(idx, str(index_dir / "index.faiss"))
    (index_dir / "chunks.json").write_text(json.dumps(all_chunks, ensure_ascii=False, indent=2), encoding="utf-8")

def search(index_dir: Path, embed_model_name: str, query: str, k: int = 6) -> List[Dict[str, Any]]:
    idx_path = index_dir / "index.faiss"
    chunks_path = index_dir / "chunks.json"
    if not idx_path.exists() or not chunks_path.exists():
        return []

    chunks = json.loads(chunks_path.read_text(encoding="utf-8"))
    if not chunks:
        return []

    model = SentenceTransformer(embed_model_name)
    q = model.encode([query], normalize_embeddings=True)
    q = np.asarray(q, dtype="float32")

    idx = faiss.read_index(str(idx_path))
    scores, ids = idx.search(q, k)

    out = []
    for score, i in zip(scores[0].tolist(), ids[0].tolist()):
        if i < 0 or i >= len(chunks):
            continue
        c = chunks[i]
        out.append({"score": float(score), "title": c.get("title",""), "doc_id": c.get("doc_id",""), "text": c.get("text","")})
    return out
