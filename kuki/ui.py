import streamlit as st


def glass_css():
    st.markdown(
        """
<style>
  .kuki-shell {max-width: 1100px; margin: 0 auto; padding: 28px 18px;}
  .kuki-card {
    border: 1px solid rgba(255,255,255,.14);
    background: radial-gradient(circle at 20% 20%, rgba(168,85,247,.14), rgba(0,0,0,.20) 70%);
    box-shadow: 0 30px 120px rgba(0,0,0,.65), 0 0 70px rgba(168,85,247,.25);
    border-radius: 18px;
    padding: 18px;
    backdrop-filter: blur(14px);
  }
  a.kuki-pill {
    display:inline-flex; align-items:center; gap:8px;
    padding:10px 14px; border-radius:9999px;
    border:1px solid rgba(255,255,255,.16);
    background: rgba(0,0,0,.25);
    text-decoration:none; color: #F5F3FF;
    box-shadow: 0 12px 30px rgba(0,0,0,.55);
    margin-right: 10px;
    margin-bottom: 10px;
  }
  a.kuki-pill:hover { border-color: rgba(168,85,247,.55); }
  .muted {opacity:.8}
  .tiny {font-size:.85rem; opacity:.75}
</style>
        """,
        unsafe_allow_html=True,
    )


def top_nav(active: str = "home"):
    pills = [
        ("home", "Home", "/?view=home"),
        ("chat", "Chat", "/?view=chat"),
        ("upload", "Upload", "/?view=upload"),
        ("library", "Library", "/?view=library"),
        ("mine", "My Uploads", "/?view=mine"),
        ("review", "Review", "/?view=review"),
    ]
    row = []
    for key, label, href in pills:
        dot = "" if key == active else ""
        row.append(f'<a class="kuki-pill" href="{href}">{dot} {label}</a>')
    st.markdown(" ".join(row), unsafe_allow_html=True)
