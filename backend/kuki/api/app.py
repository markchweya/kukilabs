"""FastAPI application factory."""

from __future__ import annotations

import logging
import threading
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from kuki import __version__
from kuki.config import Settings, get_settings
from kuki.ingest import ExtractionError
from kuki.library import NotFound
from kuki.llm import OllamaClient, OllamaUnavailable

log = logging.getLogger(__name__)


def create_app(settings: Settings | None = None, llm: OllamaClient | None = None) -> FastAPI:
    """Build the app. Tests pass their own settings and a fake-backed client."""
    settings = settings or get_settings()
    settings.ensure_dirs()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        # Documents uploaded while the embedding model was missing get their
        # vectors now, in a background thread so startup stays instant.
        threading.Thread(target=_backfill_embeddings, args=(app,), daemon=True).start()
        yield
        app.state.llm.close()

    app = FastAPI(
        title="Kuki",
        version=__version__,
        docs_url="/api/docs",
        openapi_url="/api/openapi.json",
        lifespan=lifespan,
    )
    app.state.settings = settings
    app.state.llm = llm or OllamaClient(settings.ollama_host, timeout=settings.request_timeout)

    # The web app runs on Vite's dev server during development. Kuki only
    # listens on localhost, so allowing local origins is enough.
    app.add_middleware(
        CORSMiddleware,
        allow_origin_regex=r"http://(localhost|127\.0\.0\.1)(:\d+)?",
        allow_methods=["*"],
        allow_headers=["*"],
    )
    _register_errors(app)

    from kuki.api.routes import ask, courses, documents, flashcards, quiz, status, study

    app.include_router(status.router)
    app.include_router(documents.router)
    app.include_router(study.router)
    app.include_router(quiz.router)
    app.include_router(flashcards.router)
    app.include_router(ask.router)
    app.include_router(courses.router)
    return app


def _register_errors(app: FastAPI) -> None:
    """Map domain errors to HTTP responses with student-readable messages."""

    def handler(status: int):
        async def respond(_request: Request, exc: Exception) -> JSONResponse:
            return JSONResponse({"detail": str(exc)}, status_code=status)

        return respond

    app.add_exception_handler(NotFound, handler(404))
    app.add_exception_handler(ValueError, handler(422))
    app.add_exception_handler(ExtractionError, handler(422))
    app.add_exception_handler(OllamaUnavailable, handler(503))


def _backfill_embeddings(app: FastAPI) -> None:
    from kuki.api.deps import open_library

    try:
        library = open_library(app.state.settings)
        try:
            count = library.embed_missing(app.state.llm)
            if count:
                log.info("Embedded %d segments that were added while offline.", count)
        finally:
            library.conn.close()
    except Exception:  # never let a background nicety crash the server
        log.exception("Embedding backfill failed")
