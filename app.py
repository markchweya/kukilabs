import streamlit as st
import os
from openai import OpenAI
from streamlit.components.v1 import html

# ---------------------------------------------------------
# 🔐 Inject your API key directly for local development
# (Delete or replace before pushing to GitHub!)
# ---------------------------------------------------------
os.environ["OPENAI_API_KEY"] = "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"

# Initialize the OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ---------------------------------------------------------
# 🪐 Streamlit Configuration
# ---------------------------------------------------------
st.set_page_config(page_title="KUKI • Galaxy", page_icon="💜", layout="wide")

# Hide Streamlit UI
st.markdown("""
<style>
#MainMenu, header, footer {visibility:hidden;}
.block-container {padding:0; margin:0;}
html, body, [class*="css"] {
  height:100%;
  width:100%;
  overflow:hidden !important;
  background: radial-gradient(circle at 50% 50%, #02000d, #000);
  font-family: 'Segoe UI', sans-serif;
}
iframe {position:fixed; inset:0; width:100vw; height:100vh; border:none;}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 🤖 Backend Logic
# ---------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hi there 👋 — I’m Kuki, your cosmic companion. Ask me anything!"}
    ]

def generate_reply(user_input):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are Kuki, a warm, witty AI who speaks like a kind, intelligent digital friend living in a galaxy."},
                *st.session_state.messages,
                {"role": "user", "content": user_input},
            ],
            temperature=0.8,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"⚠️ Error: {e}"

# ---------------------------------------------------------
# 🌌 Frontend HTML (Cinematic Galaxy Scene)
# ---------------------------------------------------------
galaxy_html = """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
html, body {
  margin: 0;
  padding: 0;
  overflow: hidden;
  background: radial-gradient(circle at 50% 50%, #02000d, #010008, #000);
  height: 100vh;
  width: 100vw;
  font-family: 'Segoe UI', sans-serif;
}

/* Stars */
canvas#stars {
  position: fixed;
  top: 0; left: 0;
  width: 100vw; height: 100vh;
  z-index: 1;
}

/* Aurora / Nebula */
.aurora {
  position: fixed;
  width: 100vw;
  height: 100vh;
  z-index: 2;
  background:
    radial-gradient(circle at 25% 30%, rgba(147,51,234,0.12), transparent 60%),
    radial-gradient(circle at 70% 60%, rgba(236,72,153,0.12), transparent 70%),
    radial-gradient(circle at 50% 90%, rgba(6,182,212,0.12), transparent 60%);
  filter: blur(120px);
  animation: drift 60s ease-in-out infinite alternate;
}
@keyframes drift {
  from { transform: translate(0, 0) scale(1); }
  to { transform: translate(-80px, 50px) scale(1.1); }
}

/* Center content */
.center {
  position: fixed;
  inset: 0;
  z-index: 3;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 20px;
  text-align: center;
  color: white;
}

/* KUKI Letters */
.kuki {
  display: flex;
  gap: 0.6rem;
  filter: drop-shadow(0 0 10px rgba(168,85,247,.3))
          drop-shadow(0 0 22px rgba(99,102,241,.16));
}
.letter {
  font-size: clamp(40px, 10vw, 90px);
  font-weight: 900;
  background: linear-gradient(90deg,#c084fc 0%,#818cf8 35%,#60a5fa 60%,#e879f9 100%);
  -webkit-background-clip: text;
  color: transparent;
  animation: float 6s ease-in-out infinite;
}
.letter:nth-child(odd) { animation-delay: 1s; }
@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

/* Button */
button {
  background: radial-gradient(circle at 30% 30%, #8b5cf6, #6366f1, #ec4899);
  border: none;
  color: white;
  padding: 14px 26px;
  border-radius: 9999px;
  font-weight: 700;
  cursor: pointer;
  box-shadow: 0 10px 34px rgba(99,102,241,.32);
  transition: 0.3s;
  z-index: 5;
}
button:hover {
  transform: scale(1.1);
  box-shadow: 0 12px 42px rgba(139,92,246,.42);
}

.caption {
  color: #bbb;
  letter-spacing: 4px;
  font-size: 0.8rem;
}
</style>
</head>
<body>
  <canvas id="stars"></canvas>
  <div class="aurora"></div>

  <div class="center">
    <div class="kuki">
      <span class="letter">K</span>
      <span class="letter">U</span>
      <span class="letter">K</span>
      <span class="letter">I</span>
    </div>

    <form action="#" method="post">
      <button type="button" onclick="window.parent.postMessage('chat_open', '*')">💬 Chat with Kuki</button>
    </form>

    <div class="caption">INTELLIGENT • KIND • YOURS</div>
  </div>

<script>
// ---- Stars ----
const cvs = document.getElementById('stars');
const ctx = cvs.getContext('2d');
function resize() {
  cvs.width = innerWidth;
  cvs.height = innerHeight;
}
addEventListener('resize', resize);
resize();

const stars = Array.from({length: 200}, () => ({
  x: Math.random() * cvs.width,
  y: Math.random() * cvs.height,
  r: Math.random() * 0.8,
  alpha: Math.random() * 0.7,
  twinkle: Math.random() * 0.04 + 0.01
}));

function animateStars() {
  ctx.clearRect(0, 0, cvs.width, cvs.height);
  for (const s of stars) {
    s.alpha += s.twinkle * (Math.random() > 0.5 ? 1 : -1);
    s.alpha = Math.min(Math.max(s.alpha, 0.1), 1);
    ctx.beginPath();
    ctx.arc(s.x, s.y, s.r, 0, Math.PI * 2);
    ctx.fillStyle = `rgba(255,255,255,${s.alpha})`;
    ctx.fill();
  }
  requestAnimationFrame(animateStars);
}
animateStars();

// ---- Mouse Parallax ----
document.addEventListener('mousemove', e => {
  const offsetX = (e.clientX / window.innerWidth - 0.5) * 20;
  const offsetY = (e.clientY / window.innerHeight - 0.5) * 20;
  document.querySelector('.kuki').style.transform =
    `translate(${offsetX}px, ${offsetY}px)`;
});
</script>
</body>
</html>
"""

# ---------------------------------------------------------
# 🪞 Render the Galaxy HTML + Chat
# ---------------------------------------------------------
html(galaxy_html, height=1000, scrolling=False)

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Chat with Kuki..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    reply = generate_reply(prompt)
    st.session_state.messages.append({"role": "assistant", "content": reply})
    with st.chat_message("assistant"):
        st.markdown(reply)
