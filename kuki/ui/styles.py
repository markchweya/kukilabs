import streamlit as st

BASE_CSS = """
<style>
#MainMenu, header, footer {visibility:hidden;}
.block-container {padding-top: 1.0rem; padding-bottom: 3.0rem;}
html, body, [class*="css"] {
  background: radial-gradient(circle at 50% 20%, #12002a 0%, #05000f 40%, #000 100%) !important;
}
.stChatMessage { border-radius: 18px; }
[data-testid="stChatMessageContent"] {
  border-radius: 18px !important;
  padding: 14px 14px !important;
}
.stButton > button {
  border-radius: 999px !important;
  border: 1px solid rgba(192,132,252,0.25) !important;
  background: rgba(10,5,18,0.55) !important;
  color: white !important;
  backdrop-filter: blur(12px) !important;
  box-shadow: 0 10px 30px rgba(0,0,0,0.4) !important;
}
.stButton > button:hover {
  border-color: rgba(192,132,252,0.7) !important;
  box-shadow: 0 0 0 3px rgba(124,58,237,0.18) !important;
}
textarea, input { border-radius: 14px !important; }
</style>
"""

def inject_base_css():
    st.markdown(BASE_CSS, unsafe_allow_html=True)
