import type { MisconceptionType, Verdict } from "../api";

// Plain-language names for the grader's misconception categories.
export const MISCONCEPTION_LABEL: Record<MisconceptionType, string> = {
  none: "No misconception",
  confused_concepts: "Mixed up two ideas",
  factual_error: "Something isn't true",
  overgeneralization: "True sometimes, not always",
  missing_step: "A step is missing",
  vague: "Too general",
  off_topic: "Answered a different question",
};

export const VERDICT_COPY: Record<Verdict, { title: string; tone: string }> = {
  correct: { title: "You've got it", tone: "text-sea" },
  partial: { title: "Nearly there", tone: "text-sun" },
  incorrect: { title: "Not quite yet", tone: "text-blush" },
};
