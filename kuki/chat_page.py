from __future__ import annotations

from datetime import datetime
from pathlib import Path
import sys
import tempfile
from typing import Any

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import streamlit as st

from kuki.core.extract import SUPPORTED_EXTENSIONS, extract_text_from_file, get_ocr_status, preview_text
from kuki.core.llm_local import LocalLLM, LocalLLMError, get_local_model_status


SYSTEM_PROMPT = """
You are Kuki, a private local AI assistant running on the user's own computer.
Be useful, direct, warm, and concise. When uploaded context is provided, use it
carefully and say when something is not present in the provided material.
Output Markdown only.
""".strip()


def _inject_chat_css() -> None:
    st.markdown(
        """
<style>
#MainMenu, header, footer {visibility:hidden;}
html, body, .stApp {
  background: #f7f7f5 !important;
  color: #141414 !important;
}
.block-container {
  max-width: 920px;
  padding: 1.1rem 1.2rem 7rem;
}
[data-testid="stSidebar"] {
  background: #101010 !important;
  border-right: 1px solid rgba(255,255,255,.08);
}
[data-testid="stSidebar"] * {
  color: #f2f2f2;
}
[data-testid="stSidebar"] .stButton > button {
  width: 100%;
  justify-content: flex-start;
  border-radius: 10px !important;
  border: 1px solid rgba(255,255,255,.10) !important;
  background: rgba(255,255,255,.06) !important;
  color: #f8f8f8 !important;
  box-shadow: none !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
  background: rgba(255,255,255,.12) !important;
  border-color: rgba(255,255,255,.22) !important;
}
.kuki-topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin: 0 0 18px;
}
.kuki-brand {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 0;
}
.kuki-logo {
  width: 34px;
  height: 34px;
  border-radius: 10px;
  background: #111;
  color: #fff;
  display: grid;
  place-items: center;
  font-weight: 800;
}
.kuki-title {
  font-weight: 760;
  font-size: 1rem;
}
.kuki-subtitle {
  color: #6b6b6b;
  font-size: .86rem;
}
.kuki-status {
  border: 1px solid #dfdfdc;
  background: #fff;
  color: #333;
  border-radius: 999px;
  padding: 7px 10px;
  font-size: .82rem;
  white-space: nowrap;
}
.kuki-empty {
  min-height: 48vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  gap: 14px;
}
.kuki-empty h1 {
  margin: 0;
  font-size: clamp(1.9rem, 4vw, 2.8rem);
  line-height: 1.05;
  letter-spacing: 0;
}
.kuki-empty p {
  margin: 0;
  color: #686868;
  max-width: 560px;
  line-height: 1.55;
}
.kuki-pills {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
  width: min(620px, 100%);
  margin-top: 10px;
}
.kuki-pill {
  text-align: left;
  padding: 12px 13px;
  border: 1px solid #e2e2df;
  border-radius: 12px;
  background: #fff;
  color: #333;
  font-size: .92rem;
}
[data-testid="stChatMessage"] {
  background: transparent !important;
  padding: 0.35rem 0 !important;
}
[data-testid="stChatMessageContent"] {
  border-radius: 18px !important;
  padding: 13px 15px !important;
  border: 1px solid #e4e4e1;
  background: #fff;
  box-shadow: 0 1px 2px rgba(0,0,0,.04);
}
[data-testid="stChatMessageContent"],
[data-testid="stChatMessageContent"] * {
  color: #1f1f1f !important;
}
[data-testid="stChatMessage"]:has([aria-label="Chat message from user"]) [data-testid="stChatMessageContent"] {
  background: #eeeeeb;
  border-color: #e2e2de;
}
[data-testid="stChatMessageAvatarUser"],
[data-testid="stChatMessageAvatarAssistant"] {
  background: #111 !important;
}
[data-testid="stChatMessageAvatarUser"] *,
[data-testid="stChatMessageAvatarAssistant"] * {
  color: #fff !important;
}
[data-testid="stBottom"] {
  background: #f7f7f5 !important;
}
[data-testid="stBottomBlockContainer"] {
  background: #f7f7f5 !important;
  padding-bottom: 1rem !important;
}
.stChatInput {
  max-width: 920px;
  margin: 0 auto;
}
[data-testid="stChatInput"] > div {
  background: #fff !important;
  border: 1px solid #d8d8d4 !important;
  border-radius: 20px !important;
  box-shadow: 0 6px 26px rgba(0,0,0,.08);
}
[data-testid="stChatInput"] div {
  background: transparent !important;
}
.stChatInput textarea {
  border-radius: 20px !important;
  border: 0 !important;
  background: #fff !important;
  color: #1f1f1f !important;
}
.stFileUploader {
  border-radius: 12px;
}
@media (max-width: 720px) {
  .block-container {
    padding-left: .75rem;
    padding-right: .75rem;
  }
  .kuki-topbar {
    align-items: flex-start;
  }
  .kuki-status {
    display: none;
  }
  .kuki-pills {
    grid-template-columns: 1fr;
  }
}
</style>
""",
        unsafe_allow_html=True,
    )


def _new_chat(title: str = "New chat") -> str:
    chat_id = f"chat-{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
    st.session_state.kuki_chats[chat_id] = {
        "title": title,
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "messages": [],
        "attachments": [],
    }
    st.session_state.kuki_active_chat_id = chat_id
    return chat_id


def _ensure_state() -> None:
    if "kuki_chats" not in st.session_state:
        st.session_state.kuki_chats = {}
    if "kuki_active_chat_id" not in st.session_state or st.session_state.kuki_active_chat_id not in st.session_state.kuki_chats:
        _new_chat()


def _active_chat() -> dict[str, Any]:
    return st.session_state.kuki_chats[st.session_state.kuki_active_chat_id]


def _short_title(text: str) -> str:
    cleaned = " ".join((text or "").split())
    if not cleaned:
        return "New chat"
    return cleaned[:36].rstrip() + ("..." if len(cleaned) > 36 else "")


def _extract_upload(uploaded_file) -> dict[str, str]:
    suffix = Path(uploaded_file.name).suffix or ".txt"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as handle:
        handle.write(uploaded_file.getvalue())
        temp_path = Path(handle.name)

    try:
        text = extract_text_from_file(temp_path)
    finally:
        temp_path.unlink(missing_ok=True)

    return {
        "name": uploaded_file.name,
        "text": text,
        "preview": preview_text(text, max_chars=420) or "No readable text was extracted.",
    }


def _build_context(chat: dict[str, Any]) -> str:
    attachments = chat.get("attachments", [])
    if not attachments:
        return ""

    chunks = []
    for item in attachments[-4:]:
        text = (item.get("text") or "").strip()
        if text:
            chunks.append(f"File: {item.get('name', 'upload')}\n{text[:5000]}")
    return "\n\n".join(chunks)


def _build_history(chat: dict[str, Any]) -> str:
    turns = []
    for message in chat["messages"][-10:]:
        role = "User" if message["role"] == "user" else "Kuki"
        turns.append(f"{role}: {message['content']}")
    return "\n\n".join(turns)


def _fallback_reply(prompt: str, chat: dict[str, Any], reason: str) -> str:
    context = _build_context(chat)
    lines = [
        "I can run this chat with the built-in local model once a GGUF model is added.",
        "",
        f"Local model status: {reason}",
    ]
    if context:
        lines.extend(
            [
                "",
                "I did process the uploaded material locally. Here is the most useful extracted preview:",
                "",
                preview_text(context, max_chars=900),
            ]
        )
    else:
        lines.extend(
            [
                "",
                "For now, I can keep the conversation UI and file extraction working, but deeper answers need the local model file.",
            ]
        )
    if prompt:
        lines.extend(["", f"Your message: {prompt}"])
    return "\n".join(lines)


def _generate_reply(prompt: str, chat: dict[str, Any]) -> tuple[str, str]:
    status = get_local_model_status()
    if not status.ready:
        return _fallback_reply(prompt, chat, status.message), status.message

    context = _build_context(chat)
    history = _build_history(chat)
    user_prompt = f"""
Uploaded context:
{context or 'None'}

Recent conversation:
{history or 'None'}

User message:
{prompt}
""".strip()

    try:
        reply = LocalLLM().generate(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt,
            temperature=0.35,
        )
    except (LocalLLMError, RuntimeError) as exc:
        return _fallback_reply(prompt, chat, str(exc)), str(exc)

    return reply or "I could not produce a response from the local model.", status.message


def _render_sidebar(model_ready: bool, model_message: str, ocr_ready: bool, ocr_message: str) -> None:
    with st.sidebar:
        st.markdown("### Kuki")
        if st.button("New chat", use_container_width=True):
            _new_chat()
            st.rerun()

        st.markdown("#### History")
        chats = list(st.session_state.kuki_chats.items())[::-1]
        for chat_id, chat in chats:
            label = chat.get("title") or "New chat"
            if st.button(label, key=f"chat:{chat_id}", use_container_width=True):
                st.session_state.kuki_active_chat_id = chat_id
                st.rerun()

        st.divider()
        st.markdown("#### Uploads")
        uploads = st.file_uploader(
            "Add files to this chat",
            type=[ext.lstrip(".") for ext in SUPPORTED_EXTENSIONS],
            accept_multiple_files=True,
            label_visibility="collapsed",
            help="Supported: images, PDFs, DOCX, PPTX, TXT, and MD.",
        )
        if uploads:
            chat = _active_chat()
            known = {item["name"] for item in chat["attachments"]}
            added = 0
            for uploaded_file in uploads:
                if uploaded_file.name in known:
                    continue
                chat["attachments"].append(_extract_upload(uploaded_file))
                added += 1
            if added:
                st.success(f"Added {added} file(s) to this chat.")
                st.rerun()

        active_attachments = _active_chat().get("attachments", [])
        for item in active_attachments[-5:]:
            st.caption(f"{item['name']}: {item['preview']}")

        st.divider()
        st.markdown("#### Local runtime")
        st.caption(f"AI: {'Ready' if model_ready else 'Needs model'}")
        st.caption(model_message)
        st.caption(f"OCR: {'Ready' if ocr_ready else 'Needs setup'}")
        st.caption(ocr_message)


def _render_empty_state() -> None:
    st.markdown(
        """
<div class="kuki-empty">
  <h1>What are we working on?</h1>
  <p>Chat with Kuki, upload notes or media, and let the local model answer from your computer when a GGUF model is available.</p>
  <div class="kuki-pills">
    <div class="kuki-pill">Summarize uploaded notes into revision points</div>
    <div class="kuki-pill">Explain a concept step by step</div>
    <div class="kuki-pill">Turn slides into exam questions</div>
    <div class="kuki-pill">Ask follow-up questions from a document</div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )


def render_chat_page(topic=None):
    _ensure_state()
    _inject_chat_css()

    model_status = get_local_model_status()
    ocr_status = get_ocr_status()
    _render_sidebar(model_status.ready, model_status.message, ocr_status.ready, ocr_status.message)

    status_text = "Local AI ready" if model_status.ready else "Add a GGUF model to enable local AI"
    st.markdown(
        f"""
<div class="kuki-topbar">
  <div class="kuki-brand">
    <div class="kuki-logo">K</div>
    <div>
      <div class="kuki-title">Kuki</div>
      <div class="kuki-subtitle">Private chat powered by your PC</div>
    </div>
  </div>
  <div class="kuki-status">{status_text}</div>
</div>
""",
        unsafe_allow_html=True,
    )

    chat = _active_chat()
    if not chat["messages"]:
        _render_empty_state()

    for message in chat["messages"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    prompt = st.chat_input("Message Kuki")
    if not prompt:
        return

    if not chat["messages"]:
        chat["title"] = _short_title(prompt)

    chat["messages"].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking locally..."):
            reply, model_message = _generate_reply(prompt, chat)
        st.markdown(reply)
        if not model_status.ready:
            st.caption(model_message)

    chat["messages"].append({"role": "assistant", "content": reply})
    st.rerun()


if __name__ == "__main__":
    render_chat_page()
