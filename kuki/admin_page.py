import streamlit as st
from kuki.core.store import save_upload, rebuild_index, list_docs, delete_doc, index_stats

def render_admin_page():
    st.subheader("Admin  Notes Library")
    st.caption("Upload notes here. Kuki will ONLY use uploaded notes (CPU mode).")

    up = st.file_uploader(
        "Upload files (PDF/DOCX/PPTX/TXT)",
        type=["pdf","docx","pptx","txt"],
        accept_multiple_files=True
    )

    if up:
        for f in up:
            save_upload(f.name, f.getvalue())
        rebuild_index()
        st.success(f"Saved {len(up)} file(s). Index rebuilt.")

    st.markdown(f"**Index:** `{index_stats()}`")

    st.divider()
    st.markdown("### Stored files")

    docs = list_docs()
    if not docs:
        st.info("No files uploaded yet.")
        return

    for d in docs:
        c1, c2, c3 = st.columns([6,2,2])
        with c1:
            st.markdown(f"**{d['name']}**  \n`{d['chars']} chars extracted`")
        with c2:
            if st.button("Preview text", key=f"prev:{d['name']}"):
                preview = "\n\n".join(d.get("chunks", [])[:2]) or "(No extractable text. If PDF is scanned, OCR is needed.)"
                st.text_area("Preview", preview, height=160, key=f"ta:{d['name']}")
        with c3:
            if st.button("Delete", key=f"del:{d['name']}"):
                delete_doc(d["name"])
                st.rerun()
