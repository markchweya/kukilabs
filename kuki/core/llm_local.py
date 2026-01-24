from __future__ import annotations
from pathlib import Path
from typing import List, Dict, Any
from llama_cpp import Llama

class LocalLLM:
    def __init__(self, model_path: Path):
        if not model_path.exists():
            raise FileNotFoundError(f"Local model not found: {model_path}")
        self.llm = Llama(
            model_path=str(model_path),
            n_ctx=4096,
            n_threads=0,
            n_gpu_layers=0
        )

    def answer(self, user_prompt: str, contexts: List[Dict[str, Any]]) -> str:
        ctx_block = "\n\n".join([f"[{i+1}] {c['title']}\n{c['text']}" for i, c in enumerate(contexts)])

        system = (
            "You are Kuki. Use ONLY the provided context. "
            "If the answer is not in the context, say you cannot find it in the uploaded notes. "
            "Keep answers clear and helpful."
        )

        prompt = f"""<|system|>
{system}
<|user|>
CONTEXT:
{ctx_block}

QUESTION:
{user_prompt}
<|assistant|>
"""
        out = self.llm(prompt, max_tokens=450, temperature=0.2, stop=["<|user|>"])
        return (out["choices"][0]["text"] or "").strip()
