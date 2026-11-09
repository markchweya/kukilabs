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


COURSES: list[Course] = [
    Course(
        id="cs50-ai",
        title="CS50's Introduction to Artificial Intelligence with Python",
        institution="Harvard University",
        instructor="Brian Yu and David J. Malan",
        subject="Computer Science",
        format="cs50_notes",
        license=CC_BY_NC_SA_4[0],
        license_url=CC_BY_NC_SA_4[1],
        homepage="https://cs50.harvard.edu/ai/",
        description="Search, knowledge, uncertainty, optimization, machine learning, neural networks and language.",
        lectures=_cs50("ai", ["Search", "Knowledge", "Uncertainty", "Optimization", "Learning", "Neural Networks", "Language"]),
    ),
    Course(
        id="cs50x",
        title="CS50's Introduction to Computer Science",
        institution="Harvard University",
        instructor="David J. Malan",
        subject="Computer Science",
        format="cs50_notes",
        license=CC_BY_NC_SA_4[0],
        license_url=CC_BY_NC_SA_4[1],
        homepage="https://cs50.harvard.edu/x/",
        description="Harvard's intro to computer science: C, algorithms, memory, data structures, Python, SQL and the web.",
        lectures=_cs50("x", [
            "Scratch", "C", "Arrays", "Algorithms", "Memory", "Data Structures",
            "Python", "SQL", "HTML, CSS, JavaScript", "Flask", "The End",
        ]),
    ),
    Course(
        id="yale-phil-181",
        title="Philosophy and the Science of Human Nature (PHIL 181)",
        institution="Yale University (Open Yale Courses)",
        instructor="Professor Tamar Gendler",
        subject="Philosophy",
        format="oyc_transcript",
        license=CC_BY_NC_SA_3[0],
        license_url=CC_BY_NC_SA_3[1],
        homepage="https://oyc.yale.edu/philosophy/phil-181",
        description="Classic philosophy read alongside modern psychology: morality, happiness, virtue, justice.",
        lectures=_oyc("philosophy/phil-181", [
            "Introduction", "The Ring of Gyges: Morality and Hypocrisy", "Parts of the Soul I",
            "Parts of the Soul II", "The Well-Ordered Soul: Happiness and Harmony",
            "The Disordered Soul: Thémis and PTSD", "Flourishing and Attachment", "Flourishing and Detachment",
            "Virtue and Habit I", "Virtue and Habit II", "Weakness of the Will and Procrastination",
            "Utilitarianism and its Critiques", "Deontology", "The Trolley Problem",
            "Empirically-informed Responses", "Philosophical Puzzles", "Punishment I", "Punishment II",
            "Contract & Commonwealth: Thomas Hobbes", "The Prisoner's Dilemma", "Equality", "Equality II",
            "Social Structures", "Censorship", "Tying up Loose Ends", "Concluding Lecture",
        ]),
    ),
    Course(
        id="yale-econ-252",
        title="Financial Markets (ECON 252, 2011)",
        institution="Yale University (Open Yale Courses)",
        instructor="Professor Robert J. Shiller",
        subject="Economics",
        format="oyc_transcript",
        license=CC_BY_NC_SA_3[0],
        license_url=CC_BY_NC_SA_3[1],
        homepage="https://oyc.yale.edu/economics/econ-252",
        description="Nobel laureate Robert Shiller on risk, markets, banks, insurance and behavioral finance.",
        lectures=_oyc("economics/econ-252-11", [
            "Introduction and What this Course Will Do for You and Your Purposes", "Risk and Financial Crises",
            "Technology and Invention in Finance", "Portfolio Diversification and Supporting Financial Institutions",
            "Insurance, the Archetypal Risk Management Institution: Its Opportunities and Vulnerabilities",
            "Guest Speaker: David Swensen", "Efficient Markets", "Theory of Debt, Its Proper Role, Leverage Cycles",
            "Corporate Stocks", "Real Estate", "Behavioral Finance and the Role of Psychology",
            "Misbehavior, Crises, Regulation and Self Regulation", "Banks", "Guest Speaker Maurice \"Hank\" Greenberg",
            "Forward and Futures Markets", "Guest Speaker Laura Cha", "Options Markets", "Monetary Policy",
            "Investment Banks", "Professional Money Managers and Their Influence",
            "Exchanges, Brokers, Dealers, Clearinghouses", "Public and Non-Profit Finance",
            "Finding Your Purpose in a World of Financial Capitalism",
        ]),
    ),
]

_BY_ID = {c.id: c for c in COURSES}


def get_course(course_id: str) -> Course:
    try:
        return _BY_ID[course_id]
    except KeyError:
        raise KeyError(f"Unknown course '{course_id}'") from None
