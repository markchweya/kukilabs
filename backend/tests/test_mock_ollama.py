"""Keep the development mock in step with the real structured-output models."""

import importlib.util
from pathlib import Path

import pytest

from kuki.study.ask import AnswerDraft
from kuki.study.flashcards import DeckDraft
from kuki.study.pack_models import PackSummaryDraft, StudyPackDraft
from kuki.study.quiz_models import GradeDraft, QuizDraft

spec = importlib.util.spec_from_file_location("mock_ollama", Path(__file__).parents[1] / "scripts" / "mock_ollama.py")
mock = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mock)

PROMPT = "SOURCES:\n[S1] (Week 4, Slide 1)\nBFS uses a queue. It explores level by level.\n\n[S2] (Week 4, Slide 2)\nDFS uses a stack and goes deep."


@pytest.mark.parametrize("model", [StudyPackDraft, PackSummaryDraft, QuizDraft, GradeDraft, DeckDraft, AnswerDraft])
def test_mock_answers_validate(model):
    model.model_validate(mock.answer(model.__name__, PROMPT))
