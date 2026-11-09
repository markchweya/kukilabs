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


def test_oyc_chapters_as_headings():
    # Some Yale courses (e.g. ECON 252) mark chapters with heading tags instead of bold text.
    html = """<div id="inline_content"><h1>Course</h1><h2>Lecture</h2>
    <h3>Chapter 1. Introduction to the Course [00:00:00]</h3><p>Welcome.</p>
    <h3>Chapter 2. Risk [01:02:03]</h3><p>Risk matters.</p></div>"""
    parsed = parse_oyc_transcript(html)
    assert [s.locator for s in parsed.segments] == ["0:00 · Introduction to the Course", "1:02:03 · Risk"]
