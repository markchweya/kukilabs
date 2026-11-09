# Testing Kuki with a real model

Unit tests use a fake Ollama, which proves the plumbing but says nothing about
whether a small local model produces useful study material. So Kuki was run
end to end against **Llama 3.2 3B Instruct (Q4_K_M)** and **nomic-embed-text
v1.5**, the default models, on a 4-core CPU with no GPU.

Ollama could not be installed in the test environment, so
`backend/scripts/llamacpp_bridge.py` served Ollama's API from llama-cpp-python:
the same inference engine and GGUF weights Ollama uses. Kuki's code ran
unchanged against it. `backend/scripts/real_model_check.py` drives every
feature on `samples/search-algorithms.pptx` and saves the output for review.

## What the first real run found

| Feature | First real output | Fix |
|---|---|---|
| Flashcards | Accurate, one precise citation each | none needed |
| Study pack | Good content, but cited the generic "What is a search problem?" slide on almost every item; "examples" restated definitions; boilerplate overview ("This study guide covers…", and after a first fix "we'll delve into… by the end you'll…"); term `A"* ` | prompt asks for the single supporting source, concrete examples or none; code drops weakly related extra citations; contrasting good/bad overview example; text cleaner |
| Quiz questions | Good open questions; concept labels were sentences, key ideas were topic labels ("Memory usage"), tags like `(Source: [S4] and [S8])` in the question | prompt examples for both fields; code shortens labels and strips tags |
| Grading | Praised things the student never said, flagged a correct answer as a misconception, mislabelled a BFS/DFS mix-up | redesigned (below) |
| Ask | Right answers, but `found=true` on "the sources don't mention this" | `found` moved after the answer in the schema; phrase backstop |

## How grading was redesigned

Each step below was a response to a measured failure on the real model.

1. **Claims are split in code**, at sentence ends and semicolons, and
   "X and Y both …" is split per subject. The model would not split answers
   itself and judged whole answers as one claim.
2. **The grader classifies each numbered claim** as supported, contradicted or
   not in the notes, with an exact-length schema and a token cap (an earlier
   request ran to the 300 s timeout appending items).
3. **Every claim is re-checked** with a narrow "does the lecture agree? quote it
   first" question. Asked as "is it false?", the model missed real errors; asked
   as "does it agree?", it kept them and rejected the false alarm "BFS uses a
   queue, not a FIFO queue".
4. **A student is only told they're wrong** when the grader flagged the claim
   and the re-check didn't clear it. One signal alone just withholds credit.
5. **Key ideas are checked separately.** The model could not match paraphrases
   ("level by level" vs "all nodes at a given depth"), so an idea counts as
   stated if a *verified-correct* claim contains its words or is close in
   embedding space. Measured cosine similarity: stated ideas ≥ 0.74, unstated
   ≤ 0.63; the threshold is 0.70. Wrong claims can never cover an idea, because
   embeddings measure topic, not truth ("both use a queue" is close to "DFS
   uses a stack").
6. **The verdict and score are computed in code** from key-idea coverage minus
   30 per contradiction, capped at 30 when nothing is right.

## Final grading results (real model)

Question: *Explain the main difference between BFS and DFS.*

| Student answer | Result |
|---|---|
| "DFS finds the shortest path because it uses a queue and explores level by level." | incorrect, 0. *You said "…", but DFS does not use a queue; it uses a stack. DFS explores one branch as deep as possible before backtracking.* |
| "BFS uses a FIFO queue so it explores level by level and finds the shallowest goal; DFS uses a stack and goes deep, so it uses less memory but may return a longer path." | **correct, 100**, both claims credited (first real run: partial 60 with an invented misconception) |
| "BFS and DFS both use a queue. BFS goes deep first." | incorrect, 0. Credits "BFS uses a queue"; *You said "DFS use a queue", but DFS uses a stack, not a queue.* |
| "BFS uses a queue." | partial, 25. Lists the three missing ideas |

## Speed (4-core CPU, no GPU)

| Task | Time |
|---|---|
| Study pack, 8-slide deck | 190–226 s |
| 4–5 quiz questions | 156–178 s |
| Grading one answer (final version) | 31–68 s |
| 8 flashcards | 95–110 s |
| Ask | 10–21 s |

A typical student laptop with Ollama, especially with Apple Silicon or a GPU,
will be faster.

## Remaining limits

* A 3B model's explanations can still be imprecise (one model answer blurred
  "complete" and "optimal"). Every claim stays linked to its source so the
  student can check.
* Claim-level checks rely on the lecture stating facts explicitly; reasoning
  that combines several slides is judged less reliably.
* Results vary between runs; the safeguards above are designed so variation
  produces less credit rather than a false accusation.
* Larger models (e.g. `llama3.1:8b`, `qwen2.5:7b`) are likely to grade better
  but were not tested here.
