import json

import streamlit as st

from kuki.admin_page import render_admin_page
from kuki.chat_page import render_chat_page
from kuki.core.extract import get_ocr_status
from kuki.core.llm_local import get_local_model_status
from kuki.core.store import index_stats

st.set_page_config(page_title="Kuki", page_icon=":brain:", layout="wide")

view = st.query_params.get("view", "chat")

if view == "chat":
    render_chat_page()
elif view == "admin":
    render_admin_page()
else:
    stats_payload = index_stats()
    stats = json.dumps(stats_payload, indent=2)
    model_status = get_local_model_status()
    ocr_status = get_ocr_status()

    html = f"""
<div style="max-width:980px;margin:0 auto;padding:30px 18px;">
  <div style="display:flex;align-items:flex-start;justify-content:space-between;gap:18px;">
    <div>
      <div style="font-weight:900;font-size:1.5rem;letter-spacing:.08em;">
        KUKI <span style="opacity:.65;font-weight:600;">Study Assistant</span>
      </div>
      <div style="margin-top:10px;max-width:760px;line-height:1.6;opacity:.85;">
        Turn raw notes into clean, structured study material locally on your CPU. Kuki supports pasted notes, note images,
        and uploaded study files, then rewrites them in Simple or Complex mode for revision.
      </div>
    </div>
    <div style="opacity:.72;">Kind  Intelligent  Yours</div>
  </div>

  <div style="margin-top:18px;display:flex;gap:12px;flex-wrap:wrap;">
    <a href="?view=chat"
       style="text-decoration:none;padding:10px 14px;border-radius:12px;
              border:1px solid rgba(255,255,255,.12);
              background:rgba(124,58,237,.14);
              color:#fff;font-weight:800;display:inline-flex;gap:8px;">
      <span>Open Kuki</span>
    </a>

    <a href="?view=admin"
       style="text-decoration:none;padding:10px 14px;border-radius:12px;
              border:1px solid rgba(255,255,255,.12);
              background:rgba(255,255,255,.06);
              color:#fff;font-weight:800;display:inline-flex;gap:8px;">
      <span>Manage Library</span>
    </a>
  </div>

  <div style="margin-top:22px;display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:14px;">
    <div style="padding:16px;border-radius:16px;background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.08);">
      <div style="font-weight:800;margin-bottom:8px;">Local CPU Model</div>
      <div style="opacity:.86;">{"Ready" if model_status.ready else "Setup needed"}</div>
      <div style="opacity:.62;margin-top:8px;font-size:.92rem;">{model_status.message}</div>
    </div>
    <div style="padding:16px;border-radius:16px;background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.08);">
      <div style="font-weight:800;margin-bottom:8px;">Image OCR</div>
      <div style="opacity:.86;">{"Ready" if ocr_status.ready else "Optional setup"}</div>
      <div style="opacity:.62;margin-top:8px;font-size:.92rem;">{ocr_status.message}</div>
    </div>
    <div style="padding:16px;border-radius:16px;background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.08);">
      <div style="font-weight:800;margin-bottom:8px;">Notes Library</div>
      <div style="opacity:.86;">{stats_payload.get("notes_count", 0)} saved files</div>
      <div style="opacity:.62;margin-top:8px;font-size:.92rem;">Kuki can store notes locally and reuse them for revision work.</div>
    </div>
  </div>

  <hr style="border:none;border-top:1px solid rgba(255,255,255,.08);margin:22px 0">

  <div style="opacity:.85;font-weight:800;margin-bottom:8px;">Index</div>
  <pre style="margin:0;padding:14px;border-radius:14px;white-space:pre-wrap;
              border:1px solid rgba(255,255,255,.10);background:rgba(0,0,0,.35);">{stats}</pre>
</div>
""".strip()

    st.markdown(html, unsafe_allow_html=True)
