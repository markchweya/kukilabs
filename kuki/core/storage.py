from __future__ import annotations
import json
import time
import uuid
from pathlib import Path
from typing import Dict, Any, List

def now_ts() -> int:
    return int(time.time())

def meta_path(uploads_dir: Path) -> Path:
    return uploads_dir / "_meta.json"

def load_meta(uploads_dir: Path) -> Dict[str, Any]:
    p = meta_path(uploads_dir)
    if not p.exists():
        return {"items": []}
    return json.loads(p.read_text(encoding="utf-8"))

def save_meta(uploads_dir: Path, meta: Dict[str, Any]) -> None:
    p = meta_path(uploads_dir)
    p.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

def add_item(uploads_dir: Path, filename: str, kind: str, stored_path: Path, extracted_text_path: Path | None) -> Dict[str, Any]:
    meta = load_meta(uploads_dir)
    item = {
        "id": str(uuid.uuid4()),
        "filename": filename,
        "kind": kind,
        "stored_path": str(stored_path),
        "extracted_text_path": str(extracted_text_path) if extracted_text_path else None,
        "created_at": now_ts(),
        "updated_at": now_ts(),
    }
    meta["items"].insert(0, item)
    save_meta(uploads_dir, meta)
    return item

def list_items(uploads_dir: Path) -> List[Dict[str, Any]]:
    return load_meta(uploads_dir).get("items", [])

def update_extracted_text_path(uploads_dir: Path, item_id: str, extracted_text_path: Path | None) -> None:
    meta = load_meta(uploads_dir)
    for it in meta.get("items", []):
        if it["id"] == item_id:
            it["extracted_text_path"] = str(extracted_text_path) if extracted_text_path else None
            it["updated_at"] = now_ts()
            break
    save_meta(uploads_dir, meta)

def delete_item(uploads_dir: Path, item_id: str) -> None:
    meta = load_meta(uploads_dir)
    items = meta.get("items", [])
    keep = []
    for it in items:
        if it["id"] == item_id:
            try:
                sp = Path(it["stored_path"])
                if sp.exists():
                    sp.unlink()
            except:
                pass
            try:
                tp = it.get("extracted_text_path")
                if tp:
                    tp2 = Path(tp)
                    if tp2.exists():
                        tp2.unlink()
            except:
                pass
        else:
            keep.append(it)
    meta["items"] = keep
    save_meta(uploads_dir, meta)
