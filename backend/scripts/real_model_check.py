"""Drive a running Kuki against a real model and save every output for review.

Uploads a file, then generates a study pack, a quiz, grades a deliberately
wrong and a good answer, makes flashcards and asks one in-notes and one
out-of-notes question. Outputs are JSON files in <out_dir> for a human to read:
model quality can't be asserted by a unit test.

usage: python scripts/real_model_check.py http://127.0.0.1:8765 out/ ../samples/search-algorithms.pptx [pack,quiz,cards,ask]
"""

import json
import sys
import time
from pathlib import Path

import httpx

api, out, upload = sys.argv[1], Path(sys.argv[2]), Path(sys.argv[3])
out.mkdir(parents=True, exist_ok=True)
c = httpx.Client(base_url=api, timeout=1800)


def save(name, data):
    (out / f"{name}.json").write_text(json.dumps(data, indent=2))


def timed(label, fn):
    t = time.time()
    r = fn()
    print(f"{label}: {time.time() - t:.0f}s", flush=True)
    r.raise_for_status()
    return r.json()


doc = c.post("/api/documents", files={"file": (upload.name, upload.read_bytes())}).json()
while doc["status"] == "processing":
    time.sleep(1)
    doc = c.get(f"/api/documents/{doc['id']}").json()
print("doc", doc["status"], doc["segment_count"], flush=True)
did = doc["id"]

steps = sys.argv[4].split(",") if len(sys.argv) > 4 else ["pack", "quiz", "cards", "ask"]

if "pack" in steps:
    save("pack", timed("pack", lambda: c.post(f"/api/documents/{did}/pack", json={"knowledge": "notes_only"})))

if "quiz" in steps:
    qs = timed("quiz", lambda: c.post(f"/api/documents/{did}/quiz", json={"count": 4}))
    save("quiz", qs)
    if qs:
        # A classic BFS/DFS mix-up, to see whether the grader names it.
        wrong = "DFS finds the shortest path because it uses a queue and explores level by level."
        target = next((q for q in qs if "DFS" in q["prompt"] or "depth" in q["prompt"].lower()), qs[0])
        save("grade_wrong", timed("grade wrong", lambda: c.post(f"/api/questions/{target['id']}/answer", json={"answer": wrong})))
        good = "BFS uses a FIFO queue so it explores level by level and finds the shallowest goal; DFS uses a stack and goes deep, so it uses less memory but may return a longer path."
        save("grade_good", timed("grade good", lambda: c.post(f"/api/questions/{target['id']}/answer", json={"answer": good})))

if "cards" in steps:
    save("cards", timed("cards", lambda: c.post(f"/api/documents/{did}/flashcards", json={"count": 8})))

if "ask" in steps:
    save("ask_in", timed("ask in-notes", lambda: c.post("/api/ask", json={"question": "Why is A* optimal?", "document_ids": [did]})))
    save("ask_out", timed("ask out-of-notes", lambda: c.post("/api/ask", json={"question": "Who invented A* and in what year?", "document_ids": [did]})))

print("done", did, flush=True)
