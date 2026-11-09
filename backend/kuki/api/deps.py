"""Request-scoped dependencies.

SQLite connections are not safe to share across threads, and FastAPI runs
sync endpoints in a thread pool, so each request opens its own connection.
Opening one is cheap (a file handle plus a version check). The Ollama client
wraps an httpx connection pool, which *is* thread-safe, so it is shared.
"""

from __future__ import annotations

from collections.abc import Iterator

from fastapi import Request

from kuki import db
from kuki.config import Settings
from kuki.library import Library
from kuki.llm import OllamaClient


def get_settings(request: Request) -> Settings:
    return request.app.state.settings


def get_llm(request: Request) -> OllamaClient:
    return request.app.state.llm


def open_library(settings: Settings) -> Library:
    return Library(db.connect(settings.db_path), settings)


def get_library(request: Request) -> Iterator[Library]:
    library = open_library(request.app.state.settings)
    try:
        yield library
    finally:
        library.conn.close()
