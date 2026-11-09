"""Ollama-compatible bridge over llama-cpp-python, for testing Kuki with a real model
where Ollama itself can't be installed (CI, locked-down sandboxes).

Serves the three endpoints Kuki uses: /api/tags, /api/chat (with JSON-schema
"format"), /api/embed. It runs the same llama.cpp engine and GGUF weights as
Ollama, so it exercises Kuki's real prompts. One request at a time, like
Ollama's default single slot. Students should use Ollama; this is for testing.

    pip install llama-cpp-python
    # Llama 3.2 3B Instruct Q4_K_M and nomic-embed-text v1.5 GGUF files from Hugging Face
    python scripts/llamacpp_bridge.py --chat llama-3.2-3b-q4.gguf --embed nomic-embed.gguf --port 11436
    OLLAMA_HOST=http://127.0.0.1:11436 python -m kuki
"""

from __future__ import annotations

import argparse
import json
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from llama_cpp import Llama

LOCK = threading.Lock()


def build(args):
    chat = Llama(model_path=args.chat, n_ctx=args.ctx, n_threads=args.threads, verbose=False)
    embed = Llama(model_path=args.embed, embedding=True, n_ctx=2048, n_threads=args.threads, verbose=False) if args.embed else None
    return chat, embed


class Handler(BaseHTTPRequestHandler):
    chat: Llama
    embedder: Llama | None
    log = []

    def _send(self, body, status=200):
        data = json.dumps(body).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path == "/api/tags":
            models = [{"name": "llama3.2:3b"}]
            if self.embedder:
                models.append({"name": "nomic-embed-text:latest"})
            return self._send({"models": models})
        self._send({"error": "not found"}, 404)

    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
        if self.path == "/api/chat":
            opts = body.get("options", {})
            kwargs = {"messages": body["messages"], "temperature": opts.get("temperature", 0.2), "max_tokens": 2048}
            if body.get("format"):
                kwargs["response_format"] = {"type": "json_object", "schema": body["format"]}
            started = time.time()
            with LOCK:
                out = self.chat.create_chat_completion(**kwargs)
            usage = out.get("usage", {})
            title = (body.get("format") or {}).get("title", "text")
            print(f"chat {title}: {usage.get('prompt_tokens')}+{usage.get('completion_tokens')} tok in {time.time()-started:.0f}s", flush=True)
            return self._send({"message": {"role": "assistant", "content": out["choices"][0]["message"]["content"]}})
        if self.path == "/api/embed":
            if not self.embedder:
                return self._send({"error": "model 'nomic-embed-text' not found"}, 404)
            with LOCK:
                vecs = [self.embedder.embed(t) for t in body.get("input", [])]
            return self._send({"embeddings": vecs})
        self._send({"error": "not found"}, 404)

    def log_message(self, *_):
        pass


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--chat", required=True)
    p.add_argument("--embed")
    p.add_argument("--port", type=int, default=11436)
    p.add_argument("--ctx", type=int, default=8192)
    p.add_argument("--threads", type=int, default=4)
    a = p.parse_args()
    Handler.chat, Handler.embedder = build(a)
    print(f"llama bridge on :{a.port}", flush=True)
    ThreadingHTTPServer(("127.0.0.1", a.port), Handler).serve_forever()
