# Architecture

Kuki is two programs that run on the student's computer: a Python API that does
all the work, and a React web app that talks to it. Ollama serves the language
model locally.

```
┌──────────── browser ────────────┐        ┌──────────── Ollama ─────────────┐
│ React app (frontend/)           │        │ llama3.2:3b     (chat)          │
│  library · packs · quiz · cards │        │ nomic-embed-text (embeddings)   │
└───────────────┬─────────────────┘        └───────────────▲─────────────────┘
                │ /api (same origin)                       │ HTTP, localhost
┌───────────────▼──────────────────────────────────────────┴─────────────────┐
│ FastAPI (backend/kuki)                                                      │
│  ingest/   file → located Segments          search/  BM25 + vectors + RRF  │
│  library   documents, segments, embeddings  study/   packs, quiz, cards,   │
│  openlib/  CS50 + Open Yale importer                 ask, insights         │
│  db        SQLite in ~/.kuki (migrations via PRAGMA user_version)          │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Reading files

Every reader returns `Segment(locator, text)`. The locator is the human address
of the text: `Slide 4`, `Page 12`, `Section: Binary Search`, `12:00-13:04`,
`16:29 · The Trolley Problem`. Oversized segments are split on paragraph and
sentence boundaries with a small overlap, and the locator gets a suffix
(`Page 3 (2/3)`) so citations stay precise.

| Format | Reader | Unit |
|---|---|---|
| PDF | pypdf | page (blank pages skipped, numbering preserved) |
| PowerPoint | python-pptx | slide, including tables, grouped shapes and speaker notes |
| Word | python-docx | heading section, plus tables |
| Text / Markdown | built-in | heading section or paragraph group |
| Photo | RapidOCR (optional) | whole image, boxes re-ordered into reading order |
| Audio / video | faster-whisper (optional) | ~1 minute window |
| CS50 notes | stdlib HTML parser | `<h2>` section |
| Open Yale transcript | stdlib HTML parser | timed chapter |

## Search

Two rankers are fused with Reciprocal Rank Fusion (k = 60):

* **BM25** over a tokenizer that keeps technical terms (`A*`, `C++`, `k-means`).
  Needs no model, so search always works.
* **Cosine similarity** over `nomic-embed-text` vectors stored as float32 blobs
  in SQLite. Brute force takes milliseconds at the scale of one student's
  library. Missing vectors are backfilled when the model becomes available.

## Generating with citations

1. Passages are shown to the model as numbered sources: `[S3] (Week 4, Slide 7)`.
2. Ollama's structured outputs constrain the reply to a small, flat JSON schema
   (pydantic → JSON Schema). Invalid output gets one repair retry that shows
   the model its own validation error.
3. Cited tags are resolved back to real segment IDs. Unknown or duplicate tags
   are dropped. An item with no valid citation is removed (*Only my notes*) or
   flagged *Not from your notes* (*Fill gaps*).
4. Long documents are processed in context-sized batches and merged **in code**,
   never by the model, so a citation can't be lost or rewritten in merging.

## Quiz grading

The grader receives the question, the model answer, its key ideas, the full
text of the cited segments and the student's answer (marked as untrusted
data). It returns a verdict, score, what the student got right, the specific
misconception, one of a fixed set of misconception types, and a Socratic nudge.
The fixed type vocabulary is what lets the Weak spots page find patterns.

## Spaced repetition

Standard SM-2: intervals 1, 6, then `interval × ease`; ease starts at 2.5,
moves by the SM-2 update rule, and never drops below 1.3. A failed card resets
its repetitions and counts a lapse. UI buttons map Again/Hard/Good/Easy to
grades 1/3/4/5.

## Fallbacks

| Missing | Behaviour |
|---|---|
| Ollama or chat model | extractive pack (verbatim, cited), recall questions from definitions, key-idea overlap grading, Ask returns passages |
| Embedding model | keyword-only search, vectors backfilled later |
| OCR / Whisper | upload rejected with the exact `pip install` command |
| Internet | everything except Open Course import works |

## Security

* Binds to `127.0.0.1`; binding elsewhere logs a warning.
* `TrustedHostMiddleware` rejects non-localhost Host headers (DNS rebinding).
* CORS allows only `localhost` origins (the Vite dev server).
* Upload filenames are stripped of paths; uploads stream to disk with a size cap.
* Static file serving cannot escape the build directory.
* Document text is wrapped as untrusted data in every prompt.
