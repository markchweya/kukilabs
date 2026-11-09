"""Data shapes for study packs.

Two families of models live here:

* `*Draft` models are what we ask the LLM to produce. They are kept small and
  flat because 3B-parameter models follow simple schemas far more reliably.
  Sources are plain tags ("S3").
* The public models are what the API returns: drafts with tags resolved into
  real `Citation`s, plus a `grounded` flag the UI uses to warn the student.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, computed_field

from kuki.study.sources import Citation

# ---- what the model writes ------------------------------------------------


class ConceptDraft(BaseModel):
    term: str = Field(description="A key term or concept name")
    explanation: str = Field(description="Plain-language explanation, 1-3 sentences")
    sources: list[str] = Field(description="Source tags like S1 that support this")


class PointDraft(BaseModel):
    point: str = Field(description="One important idea, one sentence")
    sources: list[str]


class ExampleDraft(BaseModel):
    title: str
    explanation: str = Field(description="A worked example or concrete illustration")
    sources: list[str]


class MistakeDraft(BaseModel):
    mistake: str = Field(description="A common misunderstanding students have")
    correction: str = Field(description="What is actually true")
    sources: list[str]


class StudyPackDraft(BaseModel):
    concepts: list[ConceptDraft]
    key_points: list[PointDraft]
    examples: list[ExampleDraft]
    common_mistakes: list[MistakeDraft]


class PackSummaryDraft(BaseModel):
    title: str = Field(description="Short topic title, under 8 words")
    overview: str = Field(description="2-3 sentence overview a student reads first")


# ---- what the API returns -------------------------------------------------


class Cited(BaseModel):
    citations: list[Citation]

    @computed_field  # included in API JSON so the UI can flag unsupported claims
    @property
    def grounded(self) -> bool:
        return bool(self.citations)


class Concept(Cited):
    term: str
    explanation: str


class KeyPoint(Cited):
    point: str


class Example(Cited):
    title: str
    explanation: str


class Mistake(Cited):
    mistake: str
    correction: str


class StudyPack(BaseModel):
    document_id: str
    title: str
    overview: str
    mode: Literal["ai", "extractive"] = Field(
        description="'ai' when written by the local model, 'extractive' when built without one"
    )
    model: str | None
    knowledge: Literal["notes_only", "fill_gaps"]
    concepts: list[Concept]
    key_points: list[KeyPoint]
    examples: list[Example]
    common_mistakes: list[Mistake]
    notice: str | None = None
