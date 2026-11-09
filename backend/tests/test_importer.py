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


def test_save_audio_for_offline(library):
    url = "https://oyc.yale.edu/philosophy/phil-181/lecture-14"
    audio = "https://oyc.yale.edu/sites/default/files/courses/exmp101/mp3/exmp101_01.mp3"
    seen = []

    def handler(request: httpx.Request):
        seen.append(str(request.url))
        if str(request.url) == url:
            return httpx.Response(200, text=(FIXTURES / "oyc_lecture.html").read_text())
        if str(request.url) == audio:
            return httpx.Response(200, content=b"ID3" + b"\0" * 1000)
        return httpx.Response(404)

    http = httpx.Client(transport=httpx.MockTransport(handler))
    from kuki.openlib.importer import save_audio

    doc = import_lecture(library, None, "yale-phil-181", 14, http)
    path = save_audio(library, doc.id, http)
    assert path.read_bytes().startswith(b"ID3")
    assert save_audio(library, doc.id, http) == path  # already saved: no second download
    assert seen.count(audio) == 1
    assert not list(path.parent.glob("*.part"))


def test_save_audio_requires_a_recording(library):
    from kuki.openlib.importer import save_audio

    doc_id = library.create_document(title="x", filename="x.md", kind="text")
    with pytest.raises(ImportFailed, match="no recording"):
        save_audio(library, doc_id, fake_web({}, []))
