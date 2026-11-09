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
    concept: str = Field(description="Short name of the concept tested, 1-4 words, e.g. 'BFS vs DFS'")
    question: str = Field(description="An open question asking the student to explain in their own words")
    ideal_answer: str = Field(description="A model answer, 2-4 sentences")
    key_ideas: list[str] = Field(description="2-4 facts a good answer must state, each a full sentence")
    sources: list[str]


class QuizDraft(BaseModel):
    questions: list[QuestionDraft]


class ClaimCheck(BaseModel):
    status: Literal["supported", "contradicted", "not_in_notes"] = Field(
        description="supported: the lecture says the same thing, even in other words. "
        "contradicted: the lecture says something different. not_in_notes: the lecture doesn't cover it"
    )
    correction: str = Field(max_length=300, description="If contradicted: what the lecture actually says. Otherwise empty")


class GradeDraft(BaseModel):
    """What the model writes when grading.

    The student's answer is split into numbered claims *in code* (a real 3B
    model would not split it, and judged the whole answer as one claim). The
    model only classifies each numbered claim, in order. Field order matters:
    constrained decoding writes the checks before the misconception type.
    The verdict and score are then computed in code (quiz.aggregate_grade).
    """

    checks: list[ClaimCheck] = Field(description="One check per numbered claim, in the same order")
    missing_ideas: list[str] = Field(description="Key ideas from the list that the answer does not cover, copied exactly")
    misconception_type: MisconceptionType
    nudge: str = Field(max_length=250, description="One guiding question that helps the student find the fix themselves")
    explanation: str = Field(max_length=600, description="A short correct explanation using only the lecture sources")

    @classmethod
    def schema_for(cls, claims: int, key_ideas: int) -> dict:
        """JSON schema with exactly one check per claim and at most one entry per key idea.

        Without these bounds a real 3B model kept appending items until the
        request timed out.
        """
        schema = cls.model_json_schema()
        props = schema["properties"]
        props["checks"].update(minItems=claims, maxItems=claims)
        props["missing_ideas"].update(maxItems=key_ideas)
        return schema


class ContradictionCheck(BaseModel):
    """A narrow second opinion on one claim the grader flagged as wrong.

    The quote comes first so the model has to find the relevant lecture text
    before it answers yes or no.
    """

    lecture_quote: str = Field(max_length=300, description="The exact lecture sentence about this topic")
    contradicts: bool = Field(description="True only if the quote says the claim is false")


class GradeResult(BaseModel):
    """A finished grade, from either the AI grader or the offline keyword grader."""

    verdict: Verdict
    score: int = Field(ge=0, le=100)
    got_right: list[str]
    misconception: str
    misconception_type: MisconceptionType
    nudge: str
    explanation: str


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
