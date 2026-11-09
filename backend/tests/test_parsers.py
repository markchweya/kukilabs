from pathlib import Path

from kuki.openlib.parsers import parse_cs50_notes, parse_oyc_transcript

FIXTURES = Path(__file__).parent / "fixtures"


def test_cs50_notes_sections():
    parsed = parse_cs50_notes((FIXTURES / "cs50_notes.html").read_text())
    assert [s.locator for s in parsed.segments] == ["Section: Search", "Section: Frontier"]
    assert "queue frontier gives breadth-first search" in parsed.segments[1].text
    assert parsed.audio_url is None


def test_oyc_transcript_chapters_and_audio():
    parsed = parse_oyc_transcript((FIXTURES / "oyc_lecture.html").read_text(), "https://oyc.yale.edu/x/lecture-1")
    assert [s.locator for s in parsed.segments] == [
        "0:00 · Introduction and Course Overview",
        "16:29 · The Trolley Problem",
    ]
    assert parsed.segments[0].text.startswith("Professor Example: Welcome")
    assert "Back to Top" not in parsed.segments[-1].text
    assert parsed.audio_url == "https://oyc.yale.edu/sites/default/files/courses/exmp101/mp3/exmp101_01.mp3"
