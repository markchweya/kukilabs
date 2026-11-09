from kuki.ingest.image import _reading_order


def box(x, y, w=40, h=10):
    return [[x, y], [x + w, y], [x + w, y + h], [x, y + h]]


def test_reading_order_groups_lines_and_sorts_left_to_right():
    detections = [
        [box(100, 0), "world", 0.9],
        [box(0, 2), "hello", 0.95],
        [box(0, 30), "second line", 0.9],
        [box(0, 60), "smudge", 0.2],  # low confidence: dropped
    ]
    assert _reading_order(detections) == ["hello world", "second line"]
