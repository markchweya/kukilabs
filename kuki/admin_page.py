from __future__ import annotations

from pathlib import Path

import streamlit as st

from kuki.core.extract import SUPPORTED_EXTENSIONS, extract_text_from_file, get_ocr_status, preview_text
from kuki.core.llm_local import get_local_model_status
from kuki.core.store import delete_doc, index_stats, list_docs, rebuild_index, save_upload


def render_admin_page():
    model_status = get_local_model_status()
    ocr_status = get_ocr_status()

    st.subheader("Admin  Local Notes Library")
    st.caption("Manage the local note library that Kuki can reuse for study generation and revision support.")

    col1, col2 = st.columns(2)
    with col1:
        st.info(f"CPU model: {'Ready' if model_status.ready else 'Setup needed'}")
        st.caption(model_status.message)
    with col2:
        st.info(f"OCR: {'Ready' if ocr_status.ready else 'Optional setup'}")
        st.caption(ocr_status.message)

    uploads = st.file_uploader(
        "Upload files to the library",
        type=[ext.lstrip(".") for ext in SUPPORTED_EXTENSIONS],
        accept_multiple_files=True,
        help="Image uploads use local OCR when available.",
    )

    if uploads:
        saved = []
        for uploaded_file in uploads:
            saved_path = save_upload(uploaded_file)
            saved.append(saved_path.name)
        rebuild_index()
        st.success(f"Saved {len(saved)} file(s) and rebuilt the library index.")

    st.markdown(f"**Index:** `{index_stats()}`")

    st.divider()
    st.markdown("### Stored Files")

    docs = list_docs()
    if not docs:
        st.info("No files uploaded yet.")
        return

    for doc in docs:
        path = Path(doc["path"])
        c1, c2, c3 = st.columns([6, 2, 2])
        with c1:
            st.markdown(f"**{doc['name']}**")
            st.caption(f"{doc['bytes']} bytes")
        with c2:
            if st.button("Preview", key=f"prev:{doc['name']}"):
                extracted = extract_text_from_file(path)
                st.text_area(
                    f"Preview: {doc['name']}",
                    extracted or "(No extractable text found. If this is an image, install OCR first.)",
                    height=180,
                    key=f"ta:{doc['name']}",
                )
                st.caption(preview_text(extracted))
        with c3:
            if st.button("Delete", key=f"del:{doc['name']}"):
                delete_doc(doc["name"])
                st.rerun()
