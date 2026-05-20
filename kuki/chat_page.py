from __future__ import annotations

from datetime import datetime
from pathlib import Path
import sys
import tempfile
from typing import Any

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import streamlit as st

from kuki.core.ai_engine import generate_ai_reply, get_ai_status
from kuki.core.extract import SUPPORTED_EXTENSIONS, extract_text_from_file, get_ocr_status, preview_text


SYSTEM_PROMPT = """
You are Kuki, a polished AI assistant for focused study, research, and everyday work.
Be useful, direct, warm, and concise. When uploaded context is provided, use it carefully
and say when something is not present in the provided material.
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
.kuki-thinking {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  color: #3a3a3a;
  font-weight: 500;
}
.kuki-thinking-orb {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  border: 2px solid #dadad6;
  border-top-color: #111;
  animation: kuki-spin .82s linear infinite;
}
.kuki-thinking-dots {
  display: inline-flex;
  gap: 4px;
  align-items: center;
}
.kuki-thinking-dots span {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: #111;
  opacity: .28;
  animation: kuki-pulse 1s ease-in-out infinite;
}
.kuki-thinking-dots span:nth-child(2) {
  animation-delay: .14s;
}
.kuki-thinking-dots span:nth-child(3) {
  animation-delay: .28s;
}
@keyframes kuki-spin {
  to { transform: rotate(360deg); }
}
@keyframes kuki-pulse {
  0%, 80%, 100% { opacity: .22; transform: translateY(0); }
  40% { opacity: .95; transform: translateY(-3px); }
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
    lines = ["I could not reach the AI runtime just now.", "", reason]
    if context:
        lines.extend(
            [
                "",
                "I did process the uploaded material. Here is the most useful extracted preview:",
                "",
                preview_text(context, max_chars=900),
            ]
        )
    else:
        lines.extend(
            [
                "",
                "Please make sure Ollama is running, then send the message again.",
            ]
        )
    if prompt:
        lines.extend(["", f"Your message: {prompt}"])
    return "\n".join(lines)


def _generate_reply(prompt: str, chat: dict[str, Any]) -> tuple[str, str]:
    status = get_ai_status()
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
        reply = generate_ai_reply(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt,
            model=status.model,
        )
    except Exception as exc:
        return _fallback_reply(prompt, chat, str(exc)), str(exc)

    return reply or "I could not produce a response. Please try again.", status.message


def _render_sidebar(ai_ready: bool, ai_message: str, ocr_ready: bool, ocr_message: str) -> None:
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
        st.markdown("#### System")
        st.caption(f"AI: {'Ready' if ai_ready else 'Offline'}")
        st.caption(ai_message)
        st.caption(f"OCR: {'Ready' if ocr_ready else 'Needs setup'}")
        st.caption(ocr_message)


def render_chat_page(topic=None):
    _ensure_state()
    _inject_chat_css()

    ai_status = get_ai_status()
    ocr_status = get_ocr_status()
    _render_sidebar(ai_status.ready, ai_status.message, ocr_status.ready, ocr_status.message)

    status_text = "Ready" if ai_status.ready else "AI offline"
    st.markdown(
        f"""
<div class="kuki-topbar">
  <div class="kuki-brand">
    <div class="kuki-logo">K</div>
    <div>
      <div class="kuki-title">Kuki</div>
      <div class="kuki-subtitle">AI workspace</div>
    </div>
  </div>
  <div class="kuki-status">{status_text}</div>
</div>
""",
        unsafe_allow_html=True,
    )

    chat = _active_chat()
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
        thinking = st.empty()
        thinking.markdown(
            """
<div class="kuki-thinking">
  <span class="kuki-thinking-orb"></span>
  <span>Thinking</span>
  <span class="kuki-thinking-dots"><span></span><span></span><span></span></span>
</div>
""",
            unsafe_allow_html=True,
        )
        reply, model_message = _generate_reply(prompt, chat)
        thinking.markdown(reply)
        if not ai_status.ready:
            st.caption(model_message)

    chat["messages"].append({"role": "assistant", "content": reply})
    st.rerun()


if __name__ == "__main__":
    render_chat_page()
