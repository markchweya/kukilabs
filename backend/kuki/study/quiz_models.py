"""Data shapes for quizzes and misconception feedback."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from kuki.study.sources import Citation

Verdict = Literal["correct", "partial", "incorrect"]

# A small, fixed vocabulary of misconception types lets Kuki group mistakes
# over time ("you often confuse two concepts") instead of only judging answers.
MisconceptionType = Literal[
    "none",                # the answer is right
    "confused_concepts",   # mixed up two related ideas (BFS vs DFS)
    "factual_error",       # stated something false
    "overgeneralization",  # true in one case, claimed for all
    "missing_step",        # right direction, skipped a key part of the reasoning
    "vague",               # too general to show understanding
    "off_topic",           # didn't address the question
]


# ---- what the model writes ------------------------------------------------


class QuestionDraft(BaseModel):
    concept: str = Field(description="The concept being tested, 1-4 words")
    question: str = Field(description="An open question asking the student to explain in their own words")
    ideal_answer: str = Field(description="A model answer, 2-4 sentences")
    key_ideas: list[str] = Field(description="2-4 ideas a good answer must include")
    sources: list[str]


class QuizDraft(BaseModel):
    questions: list[QuestionDraft]


class GradeDraft(BaseModel):
    verdict: Verdict
    score: int = Field(ge=0, le=100)
    got_right: list[str] = Field(description="What the student understood correctly")
    misconception: str = Field(description="The specific wrong or missing idea, in one sentence. Empty if correct")
    misconception_type: MisconceptionType
    nudge: str = Field(description="One guiding question that helps the student find the fix themselves")
    explanation: str = Field(description="A short correct explanation, shown only if the student asks")


# ---- what the API returns -------------------------------------------------


class Question(BaseModel):
    id: int
    document_id: str
    concept: str
    prompt: str
    citations: list[Citation]
    # The ideal answer and key ideas are deliberately NOT here: the API only
    # reveals them after the student has attempted the question.


class Grade(BaseModel):
    attempt_id: int
    question_id: int
    verdict: Verdict
    score: int
    got_right: list[str]
    misconception: str
    misconception_type: MisconceptionType
    nudge: str
    explanation: str
    ideal_answer: str
    key_ideas: list[str]
    citations: list[Citation]
    mode: Literal["ai", "keyword"]
