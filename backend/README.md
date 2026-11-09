# Kuki backend

FastAPI service that reads lecture material, indexes it and generates study
material with a **local** model served by [Ollama](https://ollama.com).

## Run

```bash
cd backend
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-optional.txt              # optional: photo OCR + lecture transcription

ollama pull llama3.2:3b          # study model
ollama pull nomic-embed-text     # search model (optional; keyword search works without it)

python -m kuki                   # http://127.0.0.1:8765, API docs at /api/docs
```

## Configuration

| Variable | Default | Purpose |
|---|---|---|
| `OLLAMA_HOST` | `http://localhost:11434` | Where Ollama runs |
| `KUKI_MODEL` | `llama3.2:3b` | Chat model for packs, quizzes, grading, flashcards |
| `KUKI_EMBED_MODEL` | `nomic-embed-text` | Embedding model for semantic search |
| `KUKI_NUM_CTX` | `8192` | Context window requested from Ollama |
| `KUKI_DATA_DIR` | `~/.kuki` | Database and uploads (outside the repo on purpose) |
| `KUKI_WHISPER_MODEL` | `base` | faster-whisper size for recordings |
| `KUKI_MAX_UPLOAD_MB` | `200` | Upload size limit |
| `KUKI_ALLOW_DOWNLOADS` | `1` | Set `0` to disable the Open Course Library importer |

## Layout

```
kuki/
  config.py          settings from environment
  db.py              SQLite + versioned migrations
  library.py         documents, segments, embeddings, search
  llm/ollama.py      Ollama HTTP client (structured output, retries)
  ingest/            PDF, PowerPoint, Word, text, photo OCR, audio transcription
  search/            BM25, vectors, reciprocal-rank fusion
  study/             study packs, quizzes + grading, flashcards (SM-2), Ask, insights
  openlib/           Harvard CS50 + Open Yale Courses importer
  api/               FastAPI app and routes
scripts/
  mock_ollama.py     DEVELOPMENT ONLY fake Ollama (no model needed)
  make_sample_deck.py  builds the original demo deck in /samples
```

## Fallbacks

Kuki keeps working when parts of the stack are missing:

| Missing | What happens |
|---|---|
| Ollama / chat model | Study packs are extractive (copied from notes, still cited); quizzes become recall questions; grading uses key-idea overlap; Ask returns the best passages |
| Embedding model | Search uses BM25 keywords only; vectors are backfilled when the model appears |
| OCR / Whisper | Photos / recordings are rejected with the exact `pip install` command |

## Tests

```bash
pip install -r requirements-dev.txt
pytest
```

Tests use an in-process fake of the Ollama API, so no model is needed.
