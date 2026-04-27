from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any

from kuki.core.llm_local import LocalLLM, LocalLLMError, get_local_model_status


@dataclass(frozen=True)
class StudyOptions:
    note_title: str = ""
    learning_mode: str = "Simple"
    knowledge_policy: str = "fill_gaps"
    output_style: str = "study_sheet"
    include_practice_questions: bool = True
    include_visual_aid: bool = False
    chart_mode: str = "static"
    chart_title: str = ""
    x_axis_label: str = "Category"
    y_axis_label: str = "Value"
    extra_instructions: str = ""


@dataclass(frozen=True)
class StudyResult:
    title: str
    extracted_text: str
    output_markdown: str
    model_used: str
    model_message: str
    diagram_markdown: str
    chart_spec: dict[str, Any] | None


def _clean_text(text: str) -> str:
    text = (text or "").replace("\r\n", "\n")
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _detect_title(text: str, fallback: str = "Study Notes") -> str:
    for line in text.splitlines():
        clean = line.strip(" -\t")
        if 3 <= len(clean) <= 80:
            return clean
    return fallback


def _sentence_parts(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?])\s+|\n+", text)
    out = []
    for part in parts:
        cleaned = re.sub(r"\s+", " ", part).strip(" -")
        if cleaned:
            out.append(cleaned)
    return out


def _definitions_from_text(text: str, limit: int = 5) -> list[str]:
    definitions = []
    for line in text.splitlines():
        if ":" not in line:
            continue
        left, right = line.split(":", 1)
        left = left.strip(" -\t")
        right = right.strip()
        if 2 <= len(left) <= 40 and right:
            definitions.append(f"- **{left}:** {right}")
        if len(definitions) >= limit:
            break
    return definitions


def _key_points_from_text(text: str, limit: int = 6) -> list[str]:
    points = []
    for sentence in _sentence_parts(text):
        if len(sentence) < 25:
            continue
        points.append(f"- {sentence}")
        if len(points) >= limit:
            break
    return points


def _build_ascii_diagram(title: str, text: str) -> str:
    phrases = [item for item in _sentence_parts(text) if 12 <= len(item) <= 60][:4]
    if len(phrases) < 2:
        return ""

    lines = [f"### Diagram / Flow\n`{title}`"]
    for idx, phrase in enumerate(phrases, start=1):
        prefix = " -> " if idx > 1 else ""
        lines.append(f"{prefix}[{idx}] {phrase}")
    return "\n".join(lines)


def _extract_chart_spec(text: str, options: StudyOptions) -> dict[str, Any] | None:
    points: list[dict[str, Any]] = []

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        label_match = re.match(r"^([A-Za-z][A-Za-z0-9 /_()-]{0,40})\s*[:=-]\s*(-?\d+(?:\.\d+)?)$", line)
        if label_match:
            points.append({"label": label_match.group(1).strip(), "value": float(label_match.group(2))})
            continue

        numeric_match = re.match(r"^(\d+(?:\.\d+)?)\s*[, ]\s*(-?\d+(?:\.\d+)?)$", line)
        if numeric_match:
            points.append({"label": numeric_match.group(1), "value": float(numeric_match.group(2))})

    if len(points) < 2:
        return None

    return {
        "title": options.chart_title or f"{options.note_title or 'Notes'} Chart",
        "x_label": options.x_axis_label or "Category",
        "y_label": options.y_axis_label or "Value",
        "mode": options.chart_mode,
        "points": points[:12],
    }


def _build_prompt(text: str, options: StudyOptions) -> tuple[str, str]:
    title = options.note_title or _detect_title(text)

    knowledge_rule = (
        "Use only the learner's notes. Do not add outside facts. If the notes are ambiguous, say what is unclear."
        if options.knowledge_policy == "strict"
        else "Fill important gaps carefully using your own knowledge, but stay faithful to the notes."
    )
    depth_rule = (
        "Write in short sentences with simple words and quick understanding."
        if options.learning_mode == "Simple"
        else "Write with deeper explanations, exam depth, and technical detail suitable for advanced learners."
    )
    revision_rule = (
        "Shape the result as an exam revision pack with likely questions and concise model answers."
        if options.output_style == "exam_revision"
        else "Shape the result as a polished study sheet."
    )
    question_rule = (
        "Include a practice questions section."
        if options.include_practice_questions
        else "Do not include practice questions."
    )
    visual_rule = (
        "Finish with a short text-only diagram or flow section for visual learners."
        if options.include_visual_aid
        else "Do not add a diagram section."
    )

    system_prompt = (
        "You are Kuki, a local study assistant that turns messy notes into structured revision material. "
        "Be professional, calm, and not chatty. Output Markdown only."
    )
    user_prompt = f"""
Title hint: {title}
Learning mode: {options.learning_mode}
Knowledge policy: {options.knowledge_policy}
Output style: {options.output_style}
{knowledge_rule}
{depth_rule}
{revision_rule}
{question_rule}
{visual_rule}

Required section order:
1. Topic title
2. Key definitions
3. Main points
4. Step-by-step explanation
5. Examples
6. Common mistakes
7. Practice questions
8. Summary

If a section cannot be supported by the notes, keep it short and say so clearly.
Additional user instructions: {options.extra_instructions or 'None'}

NOTES:
{text[:9000]}
""".strip()
    return system_prompt, user_prompt


def _fallback_output(text: str, options: StudyOptions, reason: str) -> str:
    title = options.note_title or _detect_title(text)
    definitions = _definitions_from_text(text)
    key_points = _key_points_from_text(text)
    steps = _key_points_from_text(text, limit=4)

    example_line = "- Example details were not clearly stated in the notes." if options.knowledge_policy == "strict" else "- Build one worked example from the strongest point above when revising."
    mistakes_line = "- Watch for missing definitions, skipped steps, and copied terms that are not explained."
    summary_line = next(iter(_sentence_parts(text)), "These notes were extracted locally and need a GGUF model for deeper rewriting.")

    lines = [
        f"# {title}",
        "",
        "> Local model note: the CPU model is not ready, so Kuki is showing a structured extraction-first fallback.",
        f"> Reason: {reason}",
        "",
        "## Key Definitions",
        *(definitions or ["- No clear definitions were detected in the notes."]),
        "",
        "## Main Points",
        *(key_points or ["- The notes were extracted, but there is not enough text for full summarisation yet."]),
        "",
        "## Step-by-Step Explanation",
        *(steps or ["- Start by cleaning the notes and identifying the main topic."]),
        "",
        "## Examples",
        example_line,
        "",
        "## Common Mistakes",
        mistakes_line,
    ]

    if options.include_practice_questions:
        lines.extend(
            [
                "",
                "## Practice Questions",
                "- What is the central idea of these notes?",
                "- Which definition or process needs clearer explanation?",
                "- What example could you use to teach this topic to someone else?",
            ]
        )

    lines.extend(
        [
            "",
            "## Summary",
            f"- {summary_line}",
        ]
    )

    if options.include_visual_aid:
        diagram = _build_ascii_diagram(title, text)
        if diagram:
            lines.extend(["", diagram])

    return "\n".join(lines).strip()


def generate_study_result(text: str, options: StudyOptions) -> StudyResult:
    cleaned = _clean_text(text)
    title = options.note_title or _detect_title(cleaned)
    status = get_local_model_status()
    diagram = _build_ascii_diagram(title, cleaned) if options.include_visual_aid else ""
    chart_spec = _extract_chart_spec(cleaned, options)

    if not cleaned:
        return StudyResult(
            title=title,
            extracted_text="",
            output_markdown="Kuki could not find any readable text in that input yet.",
            model_used="none",
            model_message="No text was extracted from the note.",
            diagram_markdown="",
            chart_spec=None,
        )

    if not status.ready:
        return StudyResult(
            title=title,
            extracted_text=cleaned,
            output_markdown=_fallback_output(cleaned, options, status.message),
            model_used="fallback",
            model_message=status.message,
            diagram_markdown=diagram,
            chart_spec=chart_spec,
        )

    try:
        llm = LocalLLM()
        system_prompt, user_prompt = _build_prompt(cleaned, options)
        output = llm.generate(system_prompt=system_prompt, user_prompt=user_prompt)
        if not output:
            raise LocalLLMError("The local model returned an empty response.")
        return StudyResult(
            title=title,
            extracted_text=cleaned,
            output_markdown=output,
            model_used=status.backend,
            model_message=status.message,
            diagram_markdown=diagram,
            chart_spec=chart_spec,
        )
    except Exception as exc:
        return StudyResult(
            title=title,
            extracted_text=cleaned,
            output_markdown=_fallback_output(cleaned, options, str(exc)),
            model_used="fallback",
            model_message=str(exc),
            diagram_markdown=diagram,
            chart_spec=chart_spec,
        )
