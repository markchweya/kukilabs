from __future__ import annotations

from pathlib import Path
import sys
import tempfile

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import streamlit as st

from kuki.core.extract import SUPPORTED_EXTENSIONS, extract_text_from_file, get_ocr_status, preview_text
from kuki.core.llm_local import get_local_model_status
from kuki.core.store import list_docs, rebuild_index, save_upload
from kuki.core.study import StudyOptions, generate_study_result
from kuki.ui.styles import inject_base_css


def _ensure_state() -> None:
    if "last_result" not in st.session_state:
        st.session_state.last_result = None


def _render_chart(chart_spec: dict) -> None:
    if not chart_spec:
        return

    st.markdown("### Chart")
    try:
        import altair as alt

        chart = (
            alt.Chart(alt.Data(values=chart_spec["points"]))
            .mark_line(point=True)
            .encode(
                x=alt.X("label:N", title=chart_spec["x_label"]),
                y=alt.Y("value:Q", title=chart_spec["y_label"]),
                tooltip=["label:N", "value:Q"],
            )
            .properties(title=chart_spec["title"])
        )
        st.altair_chart(chart, use_container_width=True)
    except Exception:
        st.table(chart_spec["points"])


def _extract_from_library(selected_name: str) -> tuple[str, str]:
    for doc in list_docs():
        if doc["name"] == selected_name:
            path = Path(doc["path"])
            return path.stem, extract_text_from_file(path)
    return "", ""


def _extract_from_upload(uploaded_file, save_to_library: bool) -> tuple[str, str]:
    note_title = Path(uploaded_file.name).stem

    if save_to_library:
        saved_path = save_upload(uploaded_file)
        rebuild_index()
        return note_title, extract_text_from_file(saved_path)

    suffix = Path(uploaded_file.name).suffix or ".txt"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as handle:
        handle.write(uploaded_file.getvalue())
        temp_path = Path(handle.name)

    try:
        return note_title, extract_text_from_file(temp_path)
    finally:
        temp_path.unlink(missing_ok=True)


def render_chat_page(topic=None):
    _ensure_state()
    inject_base_css()

    model_status = get_local_model_status()
    ocr_status = get_ocr_status()
    library_docs = list_docs()

    st.markdown(
        """
        <div style="display:flex;align-items:flex-start;justify-content:space-between;gap:18px;margin:10px 0 20px 0;">
          <div>
            <div style="font-weight:900;font-size:1.35rem;letter-spacing:.06em;">
              KUKI <span style="opacity:.68;font-weight:600;">Study Assistant</span>
            </div>
            <div style="opacity:.82;max-width:760px;margin-top:8px;line-height:1.5;">
              Turn handwritten notes, class slides, pasted text, and revision snippets into polished study material locally on your CPU.
            </div>
          </div>
          <div style="opacity:.7;font-size:.95rem;white-space:nowrap;">Kind  Intelligent  Yours</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.sidebar:
        st.markdown("### Local Runtime")
        st.caption(f"Model: {'Ready' if model_status.ready else 'Setup needed'}")
        st.caption(model_status.message)
        st.caption(f"OCR: {'Ready' if ocr_status.ready else 'Optional setup'}")
        st.caption(ocr_status.message)
        st.divider()
        st.markdown("### Notes Library")
        st.caption(f"Saved items: {len(library_docs)}")
        st.caption("Use the Admin page to manage your longer-term note library.")

    with st.form("kuki-study-form"):
        source_mode = st.radio("Source", ["Upload file", "Paste notes", "Library"], horizontal=True)

        uploaded_file = None
        selected_library = ""
        pasted_text = ""

        if source_mode == "Upload file":
            uploaded_file = st.file_uploader(
                "Upload a note image or document",
                type=[ext.lstrip(".") for ext in SUPPORTED_EXTENSIONS],
                help="Supported: PNG, JPG, WEBP, PDF, DOCX, PPTX, TXT, MD",
            )
            save_to_library = st.checkbox("Save this upload to the library", value=True)
        else:
            save_to_library = False

        if source_mode == "Paste notes":
            pasted_text = st.text_area(
                "Paste raw notes",
                height=220,
                placeholder="Paste short class notes, revision points, or OCR text here...",
            )

        if source_mode == "Library":
            if library_docs:
                selected_library = st.selectbox("Choose a saved note", [doc["name"] for doc in library_docs])
            else:
                st.info("The library is empty. Upload notes in Admin first.")

        col1, col2, col3 = st.columns(3)
        with col1:
            learning_mode = st.selectbox("Learning mode", ["Simple", "Complex"])
        with col2:
            knowledge_policy = st.selectbox(
                "Knowledge use",
                [("Fill gaps and add examples", "fill_gaps"), ("Only use the notes", "strict")],
                format_func=lambda item: item[0],
            )[1]
        with col3:
            output_style = st.selectbox(
                "Output style",
                [("Study sheet", "study_sheet"), ("Exam revision pack", "exam_revision")],
                format_func=lambda item: item[0],
            )[1]

        include_practice_questions = st.checkbox("Include practice questions", value=True)
        include_visual_aid = st.checkbox("Include a diagram / flow section", value=True)

        st.markdown("### Graph Options")
        chart_mode = st.radio("Chart presentation", ["Static", "Interactive"], horizontal=True)
        chart_cols = st.columns(3)
        with chart_cols[0]:
            chart_title = st.text_input("Chart title", value="Kuki Notes Chart")
        with chart_cols[1]:
            x_axis_label = st.text_input("X-axis label", value="Category")
        with chart_cols[2]:
            y_axis_label = st.text_input("Y-axis label", value="Value")

        extra_instructions = st.text_area(
            "Extra instructions",
            height=90,
            placeholder="Examples: Ask me questions where the notes are ambiguous. Fill gaps and add examples.",
        )

        submitted = st.form_submit_button("Generate Study Material", use_container_width=True)

    if submitted:
        note_title = ""
        extracted_text = ""

        if source_mode == "Upload file":
            if uploaded_file is None:
                st.warning("Upload a file first so Kuki has something to work on.")
                return
            note_title, extracted_text = _extract_from_upload(uploaded_file, save_to_library)
            if uploaded_file.name.lower().endswith((".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tif", ".tiff")) and not ocr_status.ready:
                st.info("Image OCR is not installed yet, so image extraction will stay blank until rapidocr-onnxruntime is added.")
        elif source_mode == "Paste notes":
            note_title = "Pasted Notes"
            extracted_text = pasted_text
        else:
            note_title, extracted_text = _extract_from_library(selected_library)

        options = StudyOptions(
            note_title=note_title,
            learning_mode=learning_mode,
            knowledge_policy=knowledge_policy,
            output_style=output_style,
            include_practice_questions=include_practice_questions,
            include_visual_aid=include_visual_aid,
            chart_mode=chart_mode.lower(),
            chart_title=chart_title,
            x_axis_label=x_axis_label,
            y_axis_label=y_axis_label,
            extra_instructions=extra_instructions.strip(),
        )

        with st.spinner("Kuki is processing your notes locally on CPU..."):
            st.session_state.last_result = generate_study_result(extracted_text, options)

    result = st.session_state.last_result
    if not result:
        st.info("Choose a source, then ask Kuki to generate a study sheet or exam revision pack.")
        return

    status_label = "Local CPU model" if result.model_used != "fallback" else "Fallback mode"
    st.caption(f"{status_label}: {result.model_message}")

    st.markdown("## Structured Output")
    st.markdown(result.output_markdown)

    if result.diagram_markdown and "### Diagram / Flow" not in result.output_markdown:
        st.markdown(result.diagram_markdown)

    if result.chart_spec:
        _render_chart(result.chart_spec)

    with st.expander("Extracted source text", expanded=False):
        st.text_area("Preview", result.extracted_text or "(No text extracted yet.)", height=220)
        st.caption(preview_text(result.extracted_text))


if __name__ == "__main__":
    render_chat_page()
