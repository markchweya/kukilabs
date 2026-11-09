#!/usr/bin/env bash
# Start Kuki on macOS / Linux: sets up Python, builds the web app once, runs the server.
#   ./run.sh            start Kuki at http://127.0.0.1:8765
#   ./run.sh --full     also install optional photo OCR + recording transcription
set -euo pipefail
cd "$(dirname "$0")"

if [ ! -d backend/.venv ]; then
  echo "Setting up Python environment (first run only)…"
  python3 -m venv backend/.venv
fi
backend/.venv/bin/pip install -q -r backend/requirements.txt
if [ "${1:-}" = "--full" ]; then
  backend/.venv/bin/pip install -q -r backend/requirements-optional.txt
  shift  # the remaining arguments go to the server
fi

if [ ! -f frontend/dist/index.html ]; then
  if command -v npm >/dev/null; then
    echo "Building the web app (first run only)…"
    (cd frontend && npm ci --silent && npm run build --silent)
  else
    echo "npm not found: install Node.js 20+ to build the web app, or run the API alone." >&2
  fi
fi

if ! curl -s -o /dev/null http://127.0.0.1:11434/api/tags; then
  echo "Note: Ollama isn't running. Kuki will work in offline mode until you start it (ollama serve)."
fi

echo "Kuki is starting at http://127.0.0.1:8765"
cd backend && exec .venv/bin/python -m kuki "$@"
