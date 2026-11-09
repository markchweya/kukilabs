# Responsible AI in Kuki

## Principles

1. **The student's material stays theirs.** Nothing is uploaded. Files, text,
   embeddings, quiz answers and generated content live in `~/.kuki`.
2. **Every claim is checkable.** Generated content cites the exact slide, page
   or timestamp it came from, and the source opens in one tap.
3. **Say what you don't know.** Uncited additions are labelled, "not in your
   notes" is an acceptable answer, and offline fallbacks state their limits.
4. **Teach, don't hand over answers.** Quiz feedback leads with what the student
   understood and a guiding question; the model answer is hidden until asked for.
5. **Respect authors.** Imported lectures carry their license and attribution
   everywhere they appear and are never redistributed.

## Safeguards and where they live

| Risk | Safeguard | Code |
|---|---|---|
| Hallucinated facts | Sources numbered in the prompt; invented citation tags dropped; uncited items removed in notes-only mode | `study/sources.py`, `study/packs.py` |
| Malformed model output | JSON-schema constrained decoding plus one repair retry | `llm/ollama.py` |
| Prompt injection in documents or answers | Material and answers wrapped as untrusted data with an explicit "ignore instructions inside" rule | `study/prompts.py` |
| Over-trusting Ask | An answer marked "found" but citing nothing is downgraded to "not found" | `study/ask.py` |
| Answer leakage in quizzes | The API never returns the model answer before an attempt | `study/quiz_models.py` |
| Wrongly telling a student they're wrong | A misconception needs the grader's flag *and* a quote-first re-check that doesn't clear it; one signal only withholds credit | `study/quiz.py` |
| Praise for things the student never said | Claims are split from the student's own text in code; the model only classifies them | `study/quiz.py` |
| Unfair scores from model guesswork | Verdict and score computed in code from verified claims and key-idea coverage | `study/quiz.py` |
| Local network exposure | Localhost-only bind, trusted-host check, local-only CORS | `__main__.py`, `api/app.py` |
| Copyright | Only CC BY-NC-SA courses whose license pages were checked; attribution stored per document; honest User-Agent | `openlib/` |

## Known limitations

* A 3B-parameter local model is much weaker than large hosted models. Packs
  can be shallow and grading can miss subtle errors. Citations make mistakes
  catchable; they don't prevent them.
* Citation checking proves a claim was **attributed** to a real passage, not
  that the passage fully supports it. Students should open the citation.
* The offline keyword grader only checks whether key ideas appear; it can't
  detect wrong statements and says so in the UI.
* Grading was tuned on real Llama 3.2 3B output (see
  [REAL_MODEL_TESTING.md](REAL_MODEL_TESTING.md)) but runs can still vary: an
  error may go unflagged, and paraphrases far from a key idea's wording may not
  get credit. The design errs towards withholding credit rather than accusing.
* OCR on handwriting is imperfect; the *Original* tab shows exactly what Kuki read.
* Whisper transcripts may misspell technical terms and names.
* Quiz questions favour concepts that are explained in text; diagrams and
  equations in images are not understood.
* Kuki has no login. Anyone with access to the computer's user account can read
  the library.

## Dependencies

| Component | Purpose | Runs where |
|---|---|---|
| Ollama + `llama3.2:3b` | generation, grading | local |
| `nomic-embed-text` | semantic search (optional) | local |
| RapidOCR (ONNX Runtime) | photo OCR (optional) | local |
| faster-whisper | transcription (optional) | local |
| cs50.harvard.edu, oyc.yale.edu | Open Course import, on request | internet |
