from kuki.ingest.base import Segment, clean_text, split_long


def test_clean_text_normalises_whitespace():
    assert clean_text("  a\t\tb \r\n\r\n\r\n\nc d ") == "a b\n\nc d"


def test_short_segment_is_untouched():
    seg = Segment("Page 1", "short")
    assert split_long(seg) == [seg]


def test_long_segment_splits_with_numbered_locators():
    text = " ".join(f"Sentence number {i} is here." for i in range(200))
    parts = split_long(Segment("Page 3", text), max_chars=500, overlap=50)
    assert len(parts) > 3
    assert parts[0].locator == f"Page 3 (1/{len(parts)})"
    assert all(len(p.text) <= 500 for p in parts)
    # Pieces end on sentence boundaries, not mid-word.
    assert all(p.text.endswith(".") for p in parts[:-1])
