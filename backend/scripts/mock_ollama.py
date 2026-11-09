"""DEVELOPMENT ONLY: a stand-in for Ollama that needs no model.

Use it to work on the UI on machines that can't run a real model (CI, cloud
sandboxes). It answers Kuki's structured requests with deterministic content
assembled from the source text in the prompt, so citations are real, but the
"AI" is just string slicing. Never demo it as real model output.

    python scripts/mock_ollama.py            # listens on :11434
    OLLAMA_HOST=http://localhost:11435 python scripts/mock_ollama.py --port 11435
"""

from __future__ import annotations

import argparse
import json
import re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

MODELS = ["llama3.2:3b", "nomic-embed-text:latest"]
SOURCE = re.compile(r"\[(S\d+)\] \(([^)]*)\)\n(.*?)(?=\n\n\[S\d+\] \(|\Z)", re.S)


def sources(prompt: str) -> list[tuple[str, str, str]]:
    return [(t, loc, " ".join(body.split())) for t, loc, body in SOURCE.findall(prompt)]


def first_sentence(text: str) -> str:
    m = re.match(r"(.{20,220}?[.!?])(\s|$)", text)
    return (m.group(1) if m else text[:200]).strip()


def topic(text: str) -> str:
    words = [w for w in re.findall(r"[A-Za-z][A-Za-z\-]{3,}", text) if w.lower() not in {"this", "that", "with", "from", "have"}]
    return " ".join(words[:2]).title() or "Concept"


def answer(title: str, prompt: str) -> dict:
    src = sources(prompt) or [("S1", "notes", prompt[-300:])]
    if title == "StudyPackDraft":
        return {
            "concepts": [{"term": topic(b), "explanation": first_sentence(b), "sources": [t]} for t, _, b in src[:6]],
            "key_points": [{"point": first_sentence(b), "sources": [t]} for t, _, b in src[:8]],
            "examples": [{"title": f"From {loc}", "explanation": first_sentence(b), "sources": [t]} for t, loc, b in src[1:3]],
            "common_mistakes": [{
                "mistake": f"Treating {topic(src[0][2]).lower()} as a definition to memorise rather than an idea to apply.",
                "correction": first_sentence(src[0][2]),
                "sources": [src[0][0]],
            }],
        }
    if title == "PackSummaryDraft":
        return {"title": "Study Guide", "overview": "A summary built by the development mock, not a real model."}
    if title == "QuizDraft":
        return {"questions": [{
            "concept": topic(b),
            "question": f"In your own words, explain: {first_sentence(b)[:120]}",
            "ideal_answer": first_sentence(b),
            "key_ideas": [first_sentence(b)],
            "sources": [t],
        } for t, _, b in src[:5]]}
    if title == "GradeDraft":
        return {
            "verdict": "partial", "score": 55,
            "got_right": ["You identified the main idea."],
            "misconception": "(Mock grader) Your answer leaves out a key part of the explanation.",
            "misconception_type": "missing_step",
            "nudge": "What happens in the step between the input and the result?",
            "explanation": "This feedback comes from the development mock, not a model.",
        }
    if title == "DeckDraft":
        return {"cards": [{"front": f"What is {topic(b)}?", "back": first_sentence(b), "sources": [t]} for t, _, b in src[:10]]}
    if title == "AnswerDraft":
        t, _, b = src[0]
        return {"found": True, "answer": f"(Mock) {first_sentence(b)}", "sources": [t]}
    return {}


def embed(text: str, dim: int = 64) -> list[float]:
    vec = [0.0] * dim
    for word in re.findall(r"[a-z]+", text.lower()):
        vec[hash(word) % dim] += 1.0
    return vec


class Handler(BaseHTTPRequestHandler):
    def _send(self, body: dict, status: int = 200) -> None:
        data = json.dumps(body).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path == "/api/tags":
            return self._send({"models": [{"name": m} for m in MODELS]})
        self._send({"error": "not found"}, 404)

    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
        if self.path == "/api/embed":
            return self._send({"embeddings": [embed(t) for t in body.get("input", [])]})
        if self.path == "/api/chat":
            title = (body.get("format") or {}).get("title", "")
            prompt = body["messages"][-1]["content"]
            return self._send({"message": {"role": "assistant", "content": json.dumps(answer(title, prompt))}})
        self._send({"error": "not found"}, 404)

    def log_message(self, *_):
        pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=11434)
    args = parser.parse_args()
    print(f"Mock Ollama (DEVELOPMENT ONLY) on http://127.0.0.1:{args.port}")
    ThreadingHTTPServer(("127.0.0.1", args.port), Handler).serve_forever()
