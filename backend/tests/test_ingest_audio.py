from kuki.ingest.audio import Utterance, group_by_window, timestamp


def test_timestamp_formats():
    assert timestamp(5) == "0:05"
    assert timestamp(754.9) == "12:34"
    assert timestamp(3725) == "1:02:05"


def test_utterances_grouped_into_windows():
    utterances = [Utterance(i * 10, i * 10 + 9, f"part {i}.") for i in range(15)]  # 0..149s
    segments = group_by_window(utterances, window=60)
    assert [s.locator for s in segments] == ["0:00-0:59", "1:00-1:59", "2:00-2:29"]
    assert segments[0].text.startswith("part 0. part 1.")
