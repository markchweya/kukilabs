# Devpost submission draft: Kuki

> Fill in the [bracketed] parts before submitting. Keep every claim true to what
> the demo shows (rules 5 and 11.3).

## Project name and overview

**Kuki: Your private AI study buddy.**
Kuki turns lecture slides, notes and recordings into cited study packs,
flashcards and quizzes that find your exact misunderstanding. It runs 100%
offline on your own computer with Ollama.

## Problem and solution

**Problem.** Students have more lecture material than time: long slide decks,
handwritten notes, hour-long recordings. AI study tools help, but they need a
constant internet connection, charge per use, and send coursework to a third
party. That excludes students with expensive or unreliable data, and those whose
institutions forbid uploading course material. Most tools also *tell* students
answers instead of finding out what they misunderstand.

**Who it's for.** University students, especially where connectivity is costly
or patchy, and anyone who wants to keep their study material private.

**Solution.** Kuki runs entirely on the student's laptop. It reads slides, PDFs,
Word documents, photos of notes and lecture recordings, and turns them into:

* **Cited study packs**: every concept and point links to the exact slide, page
  or timestamp, and opens the original passage in one tap.
* **Misconception quizzes**: students explain in their own words; Kuki names
  the specific wrong or missing idea, says what they got right, and asks one
  guiding question so they correct it themselves.
* **Weak spots**: progress per concept and the student's most common *kind*
  of mistake, with a study tip for it.
* **Spaced-repetition flashcards** (SM-2), exportable to Anki.
* **Ask**: answers only from the student's notes, with citations.
* **Open Course Library**: one-click import of openly licensed Harvard CS50 and
  Open Yale Courses lectures, credited to their authors, with recordings that
  can be saved for offline listening.

## AI implementation

* **Local LLM via Ollama** (`llama3.2:3b` by default): study packs, quiz
  questions, misconception grading, flashcards and Q&A.
* **Structured outputs**: every request is constrained to a pydantic-generated
  JSON Schema, with one self-repair retry on invalid output.
* **Retrieval**: hybrid search combining BM25 with `nomic-embed-text`
  embeddings via Reciprocal Rank Fusion, stored in SQLite.
* **Citation grounding**: passages are numbered for the model; cited tags are
  resolved to real passages, invented ones are dropped, and uncited claims are
  removed or labelled.
* **Local OCR** (RapidOCR / ONNX Runtime) for photos of notes and **local
  speech-to-text** (faster-whisper) for recordings.
* **Misconception taxonomy**: the grader classifies errors (confused concepts,
  missing step, overgeneralization…) so patterns can be tracked over time.
* **Fallbacks**: without a model, Kuki still builds extractive, cited packs,
  recall quizzes and keyword-graded feedback, and says so.

Stack: Python 3.11+, FastAPI, SQLite, NumPy, pypdf, python-pptx, python-docx,
React 19, TypeScript, Vite, Tailwind CSS v4. Over 100 backend tests run in CI
against an in-process fake of the Ollama API.

## Responsible AI

Private by design (localhost only, DNS-rebinding protection, no telemetry),
citations on every claim, explicit labelling of non-sourced content, coaching
instead of answer-giving, honest offline fallbacks, and license-checked open
course content. Full list and known limitations: `docs/RESPONSIBLE_AI.md`.

## Working demo

Kuki is a local app, so the demo is the video below plus the repository.
Setup: install Ollama, `ollama pull llama3.2:3b`, then `./run.sh` (or
`.\run.ps1` on Windows) and open http://127.0.0.1:8765.
Video: [link]

## Screenshots

[Capture with a real model running: library, study pack with the source
drawer open, quiz feedback, weak spots, flashcard review, open courses.]

## Source code

https://github.com/markchweya/kukilabs (branch `kuki-2.0`)

## Built during SLAY HACKS 2026

Kuki 2.0 was written from scratch between November 7 and December 7, 2026: a
new backend, web app, design and brand. It replaces an earlier Streamlit
prototype by the same author, which is in the repository's history.
[If applicable: Built with AI coding assistance.]

## Team

[Name], solo.
