"""Shared fixtures.

Every test gets its own temporary data directory so tests never touch the
developer's real ~/.kuki library.
"""

from __future__ import annotations

import pytest

from kuki.config import Settings


@pytest.fixture()
def settings(tmp_path) -> Settings:
    s = Settings(data_dir=tmp_path / "kuki-data", ollama_host="http://ollama.test")
    s.ensure_dirs()
    return s
