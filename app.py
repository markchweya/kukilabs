import streamlit as st
import json

from kuki.chat_page import render_chat_page
from kuki.admin_page import render_admin_page
from kuki.core.store import ensure_index_ready, index_stats

st.set_page_config(page_title="Kuki", page_icon="", layout="wide")

ensure_index_ready()

view = st.query_params.get("view", "home")

if view == "chat":
    render_chat_page()
elif view == "admin":
    render_admin_page()
else:
    stats = json.dumps(index_stats(), indent=2)

    html = f"""
<div style="max-width:900px;margin:0 auto;padding:28px 18px;">

  <div style="display:flex;align-items:center;justify-content:space-between;">
    <div style="font-weight:900;font-size:1.35rem;letter-spacing:.08em;">
      KUKI <span style="opacity:.6;font-weight:600;">Assistant</span>
    </div>
    <div style="opacity:.7;">Kind  Intelligent  Yours</div>
  </div>

  <div style="margin-top:16px;display:flex;gap:12px;flex-wrap:wrap;">
    <a href="?view=chat"
       style="text-decoration:none;padding:10px 14px;border-radius:12px;
              border:1px solid rgba(255,255,255,.12);
              background:rgba(124,58,237,.14);
              color:#fff;font-weight:800;display:inline-flex;gap:8px;">
      <span>Chat</span>
    </a>

    <a href="?view=admin"
       style="text-decoration:none;padding:10px 14px;border-radius:12px;
              border:1px solid rgba(255,255,255,.12);
              background:rgba(255,255,255,.06);
              color:#fff;font-weight:800;display:inline-flex;gap:8px;">
      <span>Admin</span>
    </a>
  </div>

  <hr style="border:none;border-top:1px solid rgba(255,255,255,.08);margin:18px 0">

  <div style="opacity:.85;font-weight:800;margin-bottom:8px;">Index</div>
  <pre style="margin:0;padding:14px;border-radius:14px;white-space:pre-wrap;
              border:1px solid rgba(255,255,255,.10);background:rgba(0,0,0,.35);">{stats}</pre>

</div>
""".strip()

    st.markdown(html, unsafe_allow_html=True)
