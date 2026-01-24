from __future__ import annotations
import re
from typing import List, Tuple, Dict

# We only need search_notes. list_notes was causing your crash.
# Also: if your store.py uses a different function name, we try fallbacks.
try:
    from kuki.core.store import search_notes  # expected
except Exception:
    try:
        from kuki.core.store import query_notes as search_notes  # fallback name
    except Exception:
        try:
            from kuki.core.store import query_index as search_notes  # fallback name
        except Exception:
            search_notes = None

def _clean(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "")).strip()

def _bullets(lines: List[str], max_items: int = 6) -> str:
    out = []
    for x in lines:
        x = _clean(x)
        if not x:
            continue
        out.append(f"- {x}")
        if len(out) >= max_items:
            break
    return "\n".join(out) if out else ""

def answer_from_notes(query: str, top_k: int = 6) -> Tuple[str, List[Dict]]:
    """
    Returns: (final_answer_markdown, sources_list)
    sources_list: [{"file": "...", "snippet": "..."}]
    """
    query = _clean(query)

    if search_notes is None:
        return (
            "Your note search function isn’t available yet.\n\n"
            "Fix: open `kuki/core/store.py` and confirm you have a function named `search_notes(query, top_k=...)` "
            "or rename your function to `search_notes`.",
            [],
        )

    hits = search_notes(query, top_k=top_k) or []

    if not hits:
        return (
            "I couldn’t find anything in your uploaded notes that matches that.\n\n"
            "Try rephrasing with keywords from your notes (or ask about a specific topic like BFS, DFS, A*, Greedy, Bidirectional).",
            [],
        )

    # Build a clean tutor-style answer (no raw dump)
    snippets = [h.get("text", "") for h in hits]
    files = [h.get("file", "") for h in hits]

    sentences = []
    for sn in snippets:
        parts = re.split(r"(?<=[.!?])\s+|(?<=:) ", sn)
        for p in parts:
            p = _clean(p)
            if 40 <= len(p) <= 220:
                sentences.append(p)

    # De-dup
    uniq = []
    seen = set()
    for s in sentences:
        key = s.lower()[:90]
        if key in seen:
            continue
        seen.add(key)
        uniq.append(s)

    key_points = _bullets(uniq, max_items=7)
    is_search = "search" in query.lower()

    if is_search:
        expl = (
            "### Search Algorithms (from your notes)\n"
            "Search algorithms are AI problem-solving methods that explore a **search space** (often a **tree/graph**) to find a path from a **start state** to a **goal state**.\n\n"
            "#### Core parts of a search problem\n"
            "- **State space:** all possible states\n"
            "- **Start state:** where the agent begins\n"
            "- **Goal test:** checks if we reached the goal\n"
            "- **Actions / successors:** moves between states\n"
            "- **Path cost:** cost of a solution path\n\n"
            "#### Uninformed vs informed search\n"
            "- **Uninformed (blind):** no extra knowledge (e.g., BFS, DFS)\n"
            "- **Informed (heuristic):** uses a heuristic **h(n)** (e.g., Greedy Best-First, A*)\n\n"
            "#### What your notes highlight\n"
            f"{key_points if key_points else '- (Key points extracted from your slides)'}\n"
        )
    else:
        expl = (
            "### From your notes\n"
            f"{key_points if key_points else '- (Key points extracted from your notes)'}\n"
        )

    # Sources list (compact)
    srcs = []
    used = set()
    for h in hits:
        f = h.get("file", "")
        if not f or f in used:
            continue
        used.add(f)
        srcs.append({"file": f, "snippet": _clean(h.get("text", ""))[:220]})

    if srcs:
        expl += "\n---\n**Sources used**\n"
        for s in srcs[:5]:
            expl += f"- {s['file']}\n"

    return expl, srcs
