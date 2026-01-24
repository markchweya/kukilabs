import streamlit as st
from kuki.ui.styles import inject_base_css
from kuki.core.qa import answer_from_notes

TOPICS = [
    ("Economics", ""),
    ("Technology", ""),
    ("Communication", ""),
    ("Film", ""),
    ("Journalism", ""),
]

def _ensure_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "active_topic" not in st.session_state:
        st.session_state.active_topic = None

def render_chat_page(topic=None):
    _ensure_state()
    inject_base_css()

    if topic:
        st.session_state.active_topic = topic

    st.markdown(
        """
        <div style="display:flex;align-items:center;justify-content:space-between;gap:12px;margin:10px 0 14px 0;">
          <div style="font-weight:900;font-size:1.15rem;letter-spacing:.06em;">
            KUKI <span style="opacity:.6;font-weight:600;letter-spacing:.02em;">Assistant</span>
          </div>
          <div style="opacity:.7;font-size:.9rem;">Kind  Intelligent  Yours</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    cols = st.columns(len(TOPICS))
    for i, (name, emoji) in enumerate(TOPICS):
        with cols[i]:
            active = (st.session_state.active_topic == name)
            label = f"{emoji} {name}"
            if st.button(label, use_container_width=True, type=("primary" if active else "secondary")):
                st.session_state.active_topic = name
                st.toast(f"Focus: {name}", icon=emoji)

    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    prompt = st.chat_input("Message Kuki")
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})

        focus = st.session_state.active_topic
        prompt2 = f"[Focus: {focus}] {prompt}" if focus else prompt

        reply, _sources = answer_from_notes(prompt2, top_k=6)
        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.rerun()
