"""Round-trip tests: build real files with the same libraries, then read them."""

import docx
import pytest
from pptx import Presentation
from pptx.util import Inches

from kuki.ingest import ExtractionError, extract, kind_for


def test_slides_with_notes(tmp_path):
    deck = Presentation()
    for title, body, notes in [("BFS", "Explores level by level", "Uses a FIFO queue"), ("DFS", "Goes deep first", "")]:
        slide = deck.slides.add_slide(deck.slide_layouts[1])
        slide.shapes.title.text = title
        slide.placeholders[1].text = body
        if notes:
            slide.notes_slide.notes_text_frame.text = notes
    path = tmp_path / "search.pptx"
    deck.save(path)

    segments = extract(path)
    assert [s.locator for s in segments] == ["Slide 1", "Slide 2"]
    assert "Speaker notes: Uses a FIFO queue" in segments[0].text
    assert "Goes deep first" in segments[1].text


def test_slide_tables_are_read(tmp_path):
    deck = Presentation()
    slide = deck.slides.add_slide(deck.slide_layouts[6])
    table = slide.shapes.add_table(2, 2, Inches(1), Inches(1), Inches(4), Inches(1)).table
    table.cell(0, 0).text, table.cell(0, 1).text = "Algorithm", "Complete?"
    table.cell(1, 0).text, table.cell(1, 1).text = "BFS", "Yes"
    path = tmp_path / "t.pptx"
    deck.save(path)
    assert "BFS | Yes" in extract(path)[0].text


def test_docx_sections_by_heading(tmp_path):
    document = docx.Document()
    document.add_paragraph("Course overview text.")
    document.add_heading("Binary Search", level=1)
    document.add_paragraph("Halves the search space each step.")
    path = tmp_path / "notes.docx"
    document.save(path)

    segments = extract(path)
    assert [s.locator for s in segments] == ["Section: Introduction", "Section: Binary Search"]


def test_markdown_by_heading(tmp_path):
    path = tmp_path / "n.md"
    path.write_text("# Graphs\nNodes and edges.\n\n## Trees\nA connected acyclic graph.\n")
    assert [s.locator for s in extract(path)] == ["Section: Graphs", "Section: Trees"]


def test_plain_text_paragraph_groups(tmp_path):
    path = tmp_path / "n.txt"
    path.write_text("\n\n".join(f"Paragraph {i} text." for i in range(1, 7)))
    assert [s.locator for s in extract(path)] == ["Paragraphs 1-4", "Paragraphs 5-6"]


def test_unsupported_and_empty_files(tmp_path):
    with pytest.raises(ExtractionError, match="can't read"):
        kind_for("virus.exe")
    empty = tmp_path / "e.txt"
    empty.write_text("   ")
    with pytest.raises(ExtractionError, match="No readable text"):
        extract(empty)


def test_pdf_pages(tmp_path):
    from tests.pdf_factory import write_pdf

    path = tmp_path / "lecture.pdf"
    write_pdf(path, ["A* uses f(n) = g(n) + h(n)", "", "Admissible heuristics never overestimate"])
    segments = extract(path)
    # The blank page is skipped but page numbers stay true to the original.
    assert [s.locator for s in segments] == ["Page 1", "Page 3"]
    assert "g(n) + h(n)" in segments[0].text


def test_corrupt_pdf(tmp_path):
    path = tmp_path / "broken.pdf"
    path.write_bytes(b"%PDF-1.4 not really")
    with pytest.raises(ExtractionError):
        extract(path)
