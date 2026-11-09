"""SM-2 spaced repetition (Wozniak, 1990), the algorithm behind Anki.

Each card carries an ease factor (how easy it is for this student), an interval
in days, and a repetition count. After every review the student grades their
recall from 0 to 5 and the next review is scheduled just before they would
likely forget.

Kuki's UI exposes four buttons that map onto SM-2 grades:
    Again -> 1, Hard -> 3, Good -> 4, Easy -> 5
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

MIN_EASE = 1.3
START_EASE = 2.5

BUTTONS = {"again": 1, "hard": 3, "good": 4, "easy": 5}


@dataclass(frozen=True)
class CardState:
    ease: float = START_EASE
    interval_days: int = 0
    repetitions: int = 0
    lapses: int = 0


def review(state: CardState, grade: int) -> CardState:
    """Return the card's new state after a review graded 0-5."""
    if not 0 <= grade <= 5:
        raise ValueError("grade must be between 0 and 5")

    if grade < 3:
        # Forgotten: start the repetition sequence again, see it tomorrow.
        return CardState(
            ease=max(MIN_EASE, state.ease - 0.2),
            interval_days=1,
            repetitions=0,
            lapses=state.lapses + 1,
        )

    if state.repetitions == 0:
        interval = 1
    elif state.repetitions == 1:
        interval = 6
    else:
        interval = round(state.interval_days * state.ease)

    # The SM-2 ease update: easy answers raise ease, hard ones lower it.
    ease = state.ease + (0.1 - (5 - grade) * (0.08 + (5 - grade) * 0.02))
    return CardState(
        ease=max(MIN_EASE, round(ease, 3)),
        interval_days=max(1, interval),
        repetitions=state.repetitions + 1,
        lapses=state.lapses,
    )


def next_due(state: CardState, now: datetime) -> datetime:
    return now + timedelta(days=state.interval_days)
