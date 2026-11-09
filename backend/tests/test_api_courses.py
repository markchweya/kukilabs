from pathlib import Path

import httpx

from kuki.openlib import importer
from tests.api_helpers import make_client

FIXTURES = Path(__file__).parent / "fixtures"


def test_catalog_and_import(settings, monkeypatch):
    page = (FIXTURES / "cs50_notes.html").read_text()
    monkeypatch.setattr(
        importer, "_fetch_and_parse",
        lambda http, fmt, url: importer.PARSERS[fmt](page, url),
    )
    client, _ = make_client(settings)
    courses = client.get("/api/courses").json()
    ai = next(c for c in courses if c["id"] == "cs50-ai")
    assert ai["lectures"][0]["document_id"] is None

    doc = client.post("/api/courses/cs50-ai/lectures/0/import").json()
    assert doc["license"] == "CC BY-NC-SA 4.0" and doc["status"] == "ready"
    ai = next(c for c in client.get("/api/courses").json() if c["id"] == "cs50-ai")
    assert ai["lectures"][0]["document_id"] == doc["id"]


def test_import_errors_map_to_http(settings):
    client, _ = make_client(settings)
    assert client.post("/api/courses/nope/lectures/1/import").status_code == 422
