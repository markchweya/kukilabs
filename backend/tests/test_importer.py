from dataclasses import replace
from pathlib import Path

import httpx
import pytest

from kuki import db
from kuki.library import Library
from kuki.openlib.importer import USER_AGENT, ImportFailed, import_lecture

FIXTURES = Path(__file__).parent / "fixtures"


def fake_web(pages: dict[str, str], seen: list):
    def handler(request: httpx.Request):
        seen.append(request)
        body = pages.get(str(request.url))
        return httpx.Response(200, text=body) if body else httpx.Response(404)

    return httpx.Client(transport=httpx.MockTransport(handler))


@pytest.fixture()
def library(settings):
    return Library(db.connect(settings.db_path), settings)


def test_import_yale_lecture_with_attribution(library):
    url = "https://oyc.yale.edu/philosophy/phil-181/lecture-14"
    seen = []
    http = fake_web({url: (FIXTURES / "oyc_lecture.html").read_text()}, seen)
    doc = import_lecture(library, None, "yale-phil-181", 14, http)
    assert doc.status == "ready" and doc.kind == "web"
    assert doc.title.startswith("The Trolley Problem")
    assert doc.license == "CC BY-NC-SA 3.0" and "Tamar Gendler" in doc.attribution
    assert doc.audio_url.endswith("exmp101_01.mp3")
    assert seen[0].headers["user-agent"] == USER_AGENT

    # Importing again returns the same document without downloading.
    assert import_lecture(library, None, "yale-phil-181", 14, http).id == doc.id
    assert len(seen) == 1


def test_import_cs50_notes(library):
    url = "https://cs50.harvard.edu/ai/notes/0/"
    doc = import_lecture(library, None, "cs50-ai", 0, fake_web({url: (FIXTURES / "cs50_notes.html").read_text()}, []))
    assert doc.segment_count == 2 and doc.license == "CC BY-NC-SA 4.0"


def test_import_errors(library, settings):
    with pytest.raises(ImportFailed, match="Unknown course"):
        import_lecture(library, None, "nope", 1, fake_web({}, []))
    with pytest.raises(ImportFailed, match="no lecture"):
        import_lecture(library, None, "cs50-ai", 99, fake_web({}, []))
    with pytest.raises(ImportFailed, match="Couldn't download"):
        import_lecture(library, None, "cs50-ai", 1, fake_web({}, []))
    library.settings = replace(settings, allow_downloads=False)
    with pytest.raises(ImportFailed, match="turned off"):
        import_lecture(library, None, "cs50-ai", 1, fake_web({}, []))
