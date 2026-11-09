"""Curated catalog of openly licensed courses Kuki can import.

Every entry was checked against the publisher's own license page:

* Harvard CS50 (cs50.harvard.edu/x/license, /ai/license):
  CC BY-NC-SA 4.0.
* Open Yale Courses (oyc.yale.edu/terms, section 4):
  CC BY-NC-SA 3.0, with third-party content excluded per lecture.

Both allow non-commercial reuse with attribution, which is exactly how Kuki
uses them: a student studying on their own machine, with credit shown.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

CC_BY_NC_SA_4 = ("CC BY-NC-SA 4.0", "https://creativecommons.org/licenses/by-nc-sa/4.0/")
CC_BY_NC_SA_3 = ("CC BY-NC-SA 3.0", "https://creativecommons.org/licenses/by-nc-sa/3.0/us/")


@dataclass(frozen=True)
class Lecture:
    number: int
    title: str
    url: str


@dataclass(frozen=True)
class Course:
    id: str
    title: str
    institution: str
    instructor: str
    subject: str
    format: Literal["cs50_notes", "oyc_transcript"]
    license: str
    license_url: str
    homepage: str
    description: str
    lectures: list[Lecture] = field(default_factory=list)

    def attribution(self, lecture: Lecture) -> str:
        return (
            f"\"{lecture.title}\" from {self.title} by {self.instructor}, {self.institution}. "
            f"Licensed under {self.license}. Imported unmodified into Kuki for personal study."
        )

    def lecture(self, number: int) -> Lecture:
        for lec in self.lectures:
            if lec.number == number:
                return lec
        raise KeyError(f"{self.id} has no lecture {number}")


def _cs50(slug: str, titles: list[str]) -> list[Lecture]:
    return [Lecture(i, t, f"https://cs50.harvard.edu/{slug}/notes/{i}/") for i, t in enumerate(titles)]


def _oyc(path: str, titles: list[str]) -> list[Lecture]:
    return [Lecture(i, t, f"https://oyc.yale.edu/{path}/lecture-{i}") for i, t in enumerate(titles, start=1)]
