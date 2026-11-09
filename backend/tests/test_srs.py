from datetime import datetime

import pytest

from kuki.study.srs import BUTTONS, MIN_EASE, CardState, next_due, review


def test_good_reviews_follow_sm2_intervals():
    s = CardState()
    intervals = []
    for _ in range(4):
        s = review(s, BUTTONS["good"])
        intervals.append(s.interval_days)
    assert intervals == [1, 6, 15, 38]
    assert s.ease == pytest.approx(2.5)  # "good" (4) leaves ease unchanged


def test_easy_grows_faster_than_hard():
    easy, hard = CardState(), CardState()
    for _ in range(3):
        easy, hard = review(easy, 5), review(hard, 3)
    assert easy.interval_days > hard.interval_days
    assert easy.ease > 2.5 > hard.ease


def test_forgetting_resets_and_counts_a_lapse():
    s = review(review(review(CardState(), 4), 4), 4)
    lapsed = review(s, BUTTONS["again"])
    assert (lapsed.repetitions, lapsed.interval_days, lapsed.lapses) == (0, 1, 1)
    assert lapsed.ease < s.ease


def test_ease_has_a_floor():
    s = CardState()
    for _ in range(20):
        s = review(s, 0)
    assert s.ease == MIN_EASE


def test_bad_grade_and_due_date():
    with pytest.raises(ValueError):
        review(CardState(), 6)
    assert next_due(CardState(interval_days=6), datetime(2026, 11, 1)) == datetime(2026, 11, 7)


def test_easy_on_a_new_card_skips_ahead():
    assert review(CardState(), BUTTONS["easy"]).interval_days == 4
    assert review(CardState(), BUTTONS["good"]).interval_days == 1
