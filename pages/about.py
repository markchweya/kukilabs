import streamlit as st
from streamlit.components.v1 import html

# ---------------------------------------------------------
# 🌌 Page config (wrapped so Streamlit doesn't freak out)
# ---------------------------------------------------------
try:
    st.set_page_config(
        page_title="KUKI • About",
        page_icon="💜",
        layout="wide",
    )
except Exception:
    pass

# ---------------------------------------------------------
# 🛠 Kill Streamlit chrome & sidebar
# ---------------------------------------------------------
st.markdown("""
<style>
#MainMenu, header, footer {visibility:hidden;}
section[data-testid="stSidebar"] {display:none !important;}
.block-container {
    padding: 0 !important;
    margin: 0 !important;
}
html, body, [class*="css"] {
    height:100%;
    width:100%;
    overflow:hidden !important;
    background: radial-gradient(circle at 50% 50%, #02000d, #000);
    font-family: 'Segoe UI', system-ui, -apple-system, BlinkMacSystemFont, "Inter", sans-serif;
}
iframe {
    position:fixed;
    inset:0;
    width:100vw;
    height:100vh;
    border:none;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 🌠 Fullscreen About-page HTML
# (this matches the galaxy style + cards)
# ---------------------------------------------------------
about_html = """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
/* same variable system / background stack
   (identical to home, so it feels like one product)
*/
body {
  --bg-dark: radial-gradient(circle at 50% 50%, #02000d 0%, #010008 40%, #000 70%);
  --bg-light: radial-gradient(
      circle at 50% 15%,
      #1a0f2a 0%,
      #0d0a1a 40%,
      #000008 75%,
      #000000 100%
  );

  --kuki-dark: linear-gradient(
    90deg,
    #c084fc 0%,
    #818cf8 35%,
    #60a5fa 60%,
    #e879f9 100%
  );

  --kuki-light: radial-gradient(circle at 50% 20%,
    #ffd8a8 0%,
    #ff94c7 30%,
    #b28dff 60%,
    #6fb8ff 100%
  );

  margin: 0;
  padding: 0;
  overflow: hidden;
  background: var(--bg-dark);
  height: 100vh;
  width: 100vw;
  font-family: 'Segoe UI',system-ui,-apple-system,BlinkMacSystemFont,"Inter",sans-serif;
  color: #fff;
  transition: background 2s ease, color 2s ease;
  position: relative;
}

/* star canvas */
canvas#stars {
  position: fixed;
  top: 0; left: 0;
  width: 100vw; height: 100vh;
  z-index: 1;
  transition: opacity 2s ease;
  opacity: 1;
  pointer-events: none;
}

/* aurora fog */
.aurora {
  position: fixed;
  width: 100vw;
  height: 100vh;
  z-index: 2;
  background:
    radial-gradient(circle at 25% 30%, rgba(147,51,234,0.10), transparent 60%),
    radial-gradient(circle at 70% 60%, rgba(236,72,153,0.10), transparent 70%),
    radial-gradient(circle at 50% 90%, rgba(6,182,212,0.10), transparent 60%);
  filter: blur(120px);
  animation: drift 60s ease-in-out infinite alternate;
  mix-blend-mode: screen;
  pointer-events: none;
  transition: opacity 2s ease;
}
@keyframes drift {
  from { transform: translate(0, 0) scale(1); }
  to   { transform: translate(-80px, 50px) scale(1.1); }
}

/* sunrise horizon layers */
.horizon-wrap {
  position: fixed;
  left: 50%;
  bottom: -12vh;
  transform: translateX(-50%);
  width: 160vmax;
  height: 80vmin;
  z-index: 2;
  pointer-events: none;
  opacity: 0;
  transition: opacity 2s ease, bottom 2s ease, filter 2s ease;
  filter: blur(40px);
  mix-blend-mode: screen;
}
.horizon-ring {
  position: absolute;
  left: 50%;
  bottom: 18%;
  transform: translateX(-50%);
  width: 120vmax;
  height: 40vmin;
  border-radius: 50%;
  background: radial-gradient(
    ellipse at 50% 100%,
    rgba(255,240,200,0.85) 0%,
    rgba(255,190,120,0.55) 22%,
    rgba(255,120,200,0.35) 40%,
    rgba(120,60,180,0.15) 60%,
    rgba(0,0,10,0) 75%
  );
  filter: blur(30px);
  animation: ringPulse 6s ease-in-out infinite;
  opacity: 0.95;
}
@keyframes ringPulse {
  0%,100% { filter: blur(30px) brightness(1); }
  50%     { filter: blur(36px) brightness(1.15); }
}
.horizon-haze {
  position: absolute;
  left: 50%;
  bottom: 10%;
  transform: translateX(-50%);
  width: 140vmax;
  height: 60vmin;
  border-radius: 50%;
  background: radial-gradient(
    ellipse at 50% 80%,
    rgba(255,210,150,0.35) 0%,
    rgba(255,140,200,0.22) 30%,
    rgba(90,40,120,0.14) 55%,
    rgba(20,10,30,0.05) 70%,
    rgba(0,0,0,0) 80%
  );
  filter: blur(80px);
  opacity: 0.9;
  animation: hazeDrift 10s ease-in-out infinite alternate;
}
@keyframes hazeDrift {
  0%   { transform: translate(-50%,0) scale(1); }
  100% { transform: translate(-50%,-1vh) scale(1.03); }
}
.horizon-reflect {
  position: absolute;
  left: 50%;
  bottom: 0%;
  transform: translateX(-50%) scaleY(-1);
  width: 110vmax;
  height: 30vmin;
  border-radius: 50%;
  background: radial-gradient(
    ellipse at 50% 20%,
    rgba(255,235,200,0.18) 0%,
    rgba(255,180,120,0.12) 25%,
    rgba(255,120,200,0.06) 45%,
    rgba(60,20,80,0.03) 60%,
    rgba(0,0,0,0) 80%
  );
  filter: blur(90px);
  opacity: 0.4;
  animation: reflectPulse 8s ease-in-out infinite;
}
@keyframes reflectPulse {
  0%,100% { opacity: 0.4; filter: blur(90px); }
  50%     { opacity: 0.55; filter: blur(100px); }
}
.horizon-sweep {
  position: absolute;
  left: 50%;
  bottom: 22%;
  width: 40vmin;
  height: 4vmin;
  transform: translateX(-50%);
  background: radial-gradient(
    ellipse at 50% 50%,
    rgba(255,255,255,0.6) 0%,
    rgba(255,240,200,0.4) 30%,
    rgba(255,150,200,0.18) 60%,
    rgba(0,0,0,0) 80%
  );
  filter: blur(30px);
  opacity: 0.6;
  border-radius: 9999px;
  mix-blend-mode: screen;
  animation: sweepGlide 7s linear infinite;
}
@keyframes sweepGlide {
  0%   { transform: translateX(-60%) translateY(0) scaleX(1); opacity:0.0; }
  10%  { opacity:0.5; }
  50%  { transform: translateX(0%) translateY(-0.5vh) scaleX(1.2); opacity:0.6; }
  90%  { opacity:0.4; }
  100% { transform: translateX(60%) translateY(0) scaleX(1); opacity:0.0; }
}

/* sun bloom */
.sun-glow {
  position: fixed;
  left: 50%;
  bottom: -30vh;
  transform: translateX(-50%);
  width: 60vmin;
  height: 60vmin;
  border-radius: 50%;
  background: radial-gradient(circle at 50% 40%,
    rgba(255,255,200,0.7) 0%,
    rgba(255,200,120,0.4) 30%,
    rgba(255,150,160,0.15) 55%,
    rgba(140,60,200,0.07) 70%,
    rgba(0,0,0,0) 80%);
  filter: blur(50px);
  opacity: 0;
  z-index: 2;
  pointer-events: none;
  mix-blend-mode: screen;
  transition: opacity 2s ease, bottom 2s ease, filter 2s ease;
}

/* top center floating menu */
.menu-shell {
  position: fixed;
  top: 24px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 20;
  display: flex;
  flex-direction: column;
  align-items: center;
  pointer-events: auto;
  user-select: none;
  color: #fff;
  font-size: 0.75rem;
  line-height: 1.2;
  font-weight: 500;
}
.menu-toggle {
  position: relative;
  width: 44px;
  height: 44px;
  border-radius: 9999px;
  background: radial-gradient(circle at 30% 30%, rgba(140,120,255,.4) 0%, rgba(0,0,0,0) 70%);
  box-shadow:
    0 10px 30px rgba(0,0,0,0.7),
    0 0 30px rgba(140,120,255,.6),
    0 0 80px rgba(255,120,200,.4);
  border: 1px solid rgba(255,255,255,.15);
  backdrop-filter: blur(6px);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color:#fff;
  text-shadow:
    0 0 4px rgba(255,255,255,.8),
    0 0 12px rgba(140,120,255,.8),
    0 0 40px rgba(236,72,153,.6);
  transition: all .3s ease;
}
.menu-toggle .chevron {
  font-size: .8rem;
  line-height: 1;
  transform: translateY(0);
  transition: transform .3s ease;
}
.menu-items {
  position: relative;
  width: max-content;
  margin-top: 10px;
  pointer-events: none;
}
.menu-item {
  position: absolute;
  left: 50%;
  transform: translate(-50%, -10px) scale(.8);
  opacity: 0;
  white-space: nowrap;
  letter-spacing: .15em;
  font-size: .7rem;
  font-weight: 600;
  color: #fff;
  text-transform: uppercase;
  text-shadow:
    0 0 4px rgba(255,255,255,.9),
    0 0 10px rgba(160,120,255,.6),
    0 0 30px rgba(255,120,200,.4);
  filter:
    drop-shadow(0 0 6px rgba(160,120,255,.4))
    drop-shadow(0 0 20px rgba(255,120,200,.2));
  padding: .4rem .8rem;
  border-radius: 9999px;
  background: radial-gradient(circle at 30% 30%, rgba(0,0,0,.4) 0%, rgba(0,0,0,0) 70%);
  backdrop-filter: blur(6px);

  transition: opacity .4s ease, transform .4s ease;
  cursor: pointer;
  pointer-events: auto;
}
/* drop-down animation positions */
.menu-shell.open .menu-item:nth-child(1) {
  top: 50px;
  opacity: 1;
  transform: translate(-50%,0) scale(1);
  transition-delay: .05s;
}
.menu-shell.open .menu-item:nth-child(2) {
  top: 90px;
  opacity: 1;
  transform: translate(-50%,0) scale(1);
  transition-delay: .12s;
}
.menu-shell.open .menu-item:nth-child(3) {
  top: 130px;
  opacity: 1;
  transform: translate(-50%,0) scale(1);
  transition-delay: .19s;
}
.menu-shell.open .chevron { transform: rotate(180deg); }
.menu-shell:not(.open) .menu-items { pointer-events:none; }

/* theme toggle */
.theme-toggle {
  position: fixed;
  top: 24px;
  right: 24px;
  z-index: 20;
  background: rgba(0,0,0,0.4);
  border: 1px solid rgba(255,255,255,0.15);
  backdrop-filter: blur(6px);
  box-shadow:
    0 10px 30px rgba(0,0,0,0.6),
    0 0 20px rgba(139,92,246,0.4);
  border-radius: 9999px;
  padding: 8px 14px;
  font-size: 0.8rem;
  font-weight: 500;
  color: #fff;
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  user-select: none;
  line-height: 1;
  transition: background 0.3s ease, box-shadow 0.3s ease, color 0.3s ease;
}
.theme-toggle:hover {
  box-shadow:
    0 12px 36px rgba(0,0,0,0.7),
    0 0 28px rgba(236,72,153,0.5),
    0 0 60px rgba(99,102,241,0.4);
}
.icon-moon, .icon-sun {
  font-size: 1rem;
  line-height: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}
.icon-sun { display:none; }

/* main content wrapper */
.main-shell {
  position: fixed;
  inset: 0;
  z-index: 3;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding-top: 120px;
  padding-left: 1rem;
  padding-right: 1rem;
  color: white;
  text-align: center;
  pointer-events: none;
}

/* title "KUKI" */
.about-title {
  position: relative;
  display: flex;
  gap: 0.6rem;
  align-items: center;
  justify-content: center;
  filter:
    0 0 10px rgba(168,85,247,.3)
    drop-shadow(0 0 22px rgba(99,102,241,.16));
  transition: filter 2s ease, text-shadow 2s ease;
  pointer-events: auto;
}
.about-letter {
  font-size: clamp(28px, 6vw, 60px);
  font-weight: 900;
  background: var(--kuki-dark);
  -webkit-background-clip: text;
  color: transparent;
  text-shadow:
    0 0 8px rgba(168,85,247,.3),
    0 0 22px rgba(99,102,241,.16);
  animation: floatWord 6s ease-in-out infinite;
  transition: background 2s ease, filter 2s ease, text-shadow 2s ease;
}
.about-letter:nth-child(odd){ animation-delay:1s; }
@keyframes floatWord {
  0%,100% { transform: translateY(0); }
  50%     { transform: translateY(-10px); }
}

.subtitle-line {
  margin-top: .5rem;
  font-size: .8rem;
  letter-spacing: .35em;
  font-weight: 500;
  text-transform: uppercase;
  color: rgba(255,255,255,.7);
  text-shadow:
    0 0 6px rgba(200,180,255,0.5),
    0 0 18px rgba(120,80,255,0.3);
}

/* grid of glass cards */
.content-grid {
  pointer-events: auto;
  display: grid;
  grid-template-columns: repeat(2, minmax(min(340px,45vw), 400px));
  grid-gap: 2rem 2rem;
  margin-top: 2.5rem;
  max-width: 900px;
}
.card {
  position: relative;
  border-radius: 24px;
  padding: 1.25rem 1.25rem 1.5rem;
  background: radial-gradient(circle at 20% 20%, rgba(0,0,0,.5) 0%, rgba(0,0,0,0) 70%);
  border: 1px solid rgba(255,255,255,.08);
  box-shadow:
    0 30px 80px rgba(0,0,0,.8),
    0 0 40px rgba(140,120,255,.4),
    0 0 120px rgba(255,120,200,.25);
  backdrop-filter: blur(10px);
  color: #fff;
  text-align: left;
  min-height: 160px;
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  animation: cardFloat 6s ease-in-out infinite;
  transition: box-shadow 2s ease, background 2s ease, border 2s ease;
}
.card:nth-child(odd){ animation-delay:1s; }
.card:nth-child(even){ animation-delay:2s; }
@keyframes cardFloat {
  0%,100% { transform: translateY(0) translateZ(30px) rotateX(10deg); }
  50%     { transform: translateY(-6px) translateZ(34px) rotateX(8deg); }
}
.card-title {
  font-size: .8rem;
  font-weight: 600;
  letter-spacing: .3em;
  text-transform: uppercase;
  color: #fff;
  margin-bottom: .75rem;
  text-shadow:
    0 0 6px rgba(255,255,255,.8),
    0 0 18px rgba(160,120,255,.5),
    0 0 40px rgba(255,120,200,.3);
}
.card-body {
  font-size: .9rem;
  line-height: 1.5;
  color: rgba(255,255,255,.85);
  text-shadow:
    0 0 4px rgba(0,0,0,.8),
    0 0 16px rgba(160,120,255,.2);
}
.card-body b {
  color: rgba(255,255,255,1);
  text-shadow:
    0 0 4px rgba(255,255,255,.8),
    0 0 12px rgba(140,120,255,.4);
}
.listish {
  margin-top: .5rem;
  font-size:.9rem;
  line-height:1.5;
  color: rgba(255,255,255,.8);
}
.listish .dot {
  color: rgba(255,255,255,.9);
  margin-right:.5rem;
  text-shadow:
    0 0 6px rgba(255,255,255,.8),
    0 0 20px rgba(140,120,255,.5),
    0 0 40px rgba(255,120,200,.4);
}

/* light mode overrides */
body.light-mode {
  background: var(--bg-light);
  color: #fff;
}
body.light-mode #stars { opacity: 0.3; }
body.light-mode .aurora { opacity: 0.15; }
body.light-mode .horizon-wrap {
  opacity: 1;
  bottom: -5vh;
  filter: blur(60px);
}
body.light-mode .sun-glow {
  opacity: 1;
  bottom: 0vh;
  filter: blur(70px);
}
body.light-mode .menu-toggle {
  background: radial-gradient(circle at 30% 30%, rgba(255,230,170,.4) 0%, rgba(0,0,0,0) 70%);
  box-shadow:
    0 10px 30px rgba(0,0,0,0.6),
    0 0 30px rgba(255,200,150,.6),
    0 0 80px rgba(255,255,210,.4);
  border: 1px solid rgba(255,255,255,.4);
  color:#fff;
  text-shadow:
    0 0 4px rgba(0,0,0,.8),
    0 0 12px rgba(255,220,160,.8),
    0 0 40px rgba(255,150,200,.6);
}
body.light-mode .theme-toggle {
  background: rgba(255,255,255,0.15);
  color: #fff;
  border: 1px solid rgba(255,255,255,0.3);
  box-shadow:
    0 10px 30px rgba(255,200,160,0.4),
    0 0 20px rgba(255,255,200,0.6);
}
body.light-mode .icon-moon { display:none; }
body.light-mode .icon-sun  { display:block; }

body.light-mode .about-letter {
  background: var(--kuki-light);
  -webkit-background-clip: text;
  color: transparent;
  filter:
    drop-shadow(0 0 4px rgba(255,200,160,.4))
    drop-shadow(0 0 12px rgba(255,255,200,.25));
  text-shadow:
    0 0 2px rgba(0,0,0,0.6),
    0 1px 2px rgba(0,0,0,0.8),
    0 0 8px rgba(255,200,160,.35),
    0 0 22px rgba(255,255,200,.2);
}
body.light-mode .subtitle-line {
  color: rgba(255,255,255,.8);
  text-shadow:
    0 0 4px rgba(0,0,0,.7),
    0 0 12px rgba(255,220,180,.5),
    0 0 28px rgba(255,140,200,.3);
}
body.light-mode .card {
  background: radial-gradient(circle at 20% 20%, rgba(0,0,0,.35) 0%, rgba(0,0,0,0) 70%);
  border: 1px solid rgba(255,255,255,.18);
  box-shadow:
    0 30px 80px rgba(0,0,0,.7),
    0 0 60px rgba(255,200,150,.4),
    0 0 140px rgba(255,255,210,.35);
}
body.light-mode .card-title {
  text-shadow:
    0 0 6px rgba(0,0,0,.8),
    0 0 18px rgba(255,220,160,.5),
    0 0 40px rgba(255,150,200,.3);
}
body.light-mode .card-body,
body.light-mode .listish {
  color: rgba(255,255,255,.9);
  text-shadow:
    0 0 2px rgba(0,0,0,.8),
    0 0 12px rgba(255,220,160,.3),
    0 0 32px rgba(255,150,200,.2);
}
body.light-mode .listish .dot {
  text-shadow:
    0 0 4px rgba(0,0,0,.8),
    0 0 12px rgba(255,220,160,.5),
    0 0 32px rgba(255,150,200,.4);
}

/* responsive */
@media (max-width:900px){
  .content-grid {
    grid-template-columns: minmax(min(340px,90vw), 400px);
  }
}
@media (max-width:600px){
  .theme-toggle{
    top:16px;
    right:16px;
    font-size:.75rem;
    padding:8px 12px;
  }
  .menu-shell{ top:16px; }
  .main-shell{ padding-top:110px; }
  .about-letter{
    font-size:clamp(28px,8vw,60px);
  }
  .subtitle-line{
    letter-spacing:.25em;
    font-size:.7rem;
  }
}
</style>
</head>
<body>

  <!-- floating menu -->
  <div class="menu-shell" id="menuShell">
    <div class="menu-toggle" id="menuToggle">
      <div class="chevron">▼</div>
    </div>
    <div class="menu-items" id="menuItems">
      <div class="menu-item" data-link="/">HOME</div>
      <div class="menu-item" data-link="/About">ABOUT</div>
      <div class="menu-item" data-link="/contact">CONTACT</div>
    </div>
  </div>

  <!-- theme toggle -->
  <div class="theme-toggle" id="themeToggle">
    <div class="icon-moon">🌙</div>
    <div class="icon-sun">☀️</div>
    <div class="label">mode</div>
  </div>

  <!-- cosmic layers -->
  <canvas id="stars"></canvas>
  <div class="aurora"></div>

  <div class="horizon-wrap">
    <div class="horizon-ring"></div>
    <div class="horizon-haze"></div>
    <div class="horizon-reflect"></div>
    <div class="horizon-sweep"></div>
  </div>

  <div class="sun-glow"></div>

  <!-- ABOUT CONTENT -->
  <div class="main-shell">
    <div class="about-title">
      <span class="about-letter">K</span>
      <span class="about-letter">U</span>
      <span class="about-letter">K</span>
      <span class="about-letter">I</span>
    </div>
    <div class="subtitle-line">
      INTELLIGENT&nbsp;&nbsp;•&nbsp;&nbsp;KIND&nbsp;&nbsp;•&nbsp;&nbsp;YOURS
    </div>

    <div class="content-grid">

      <div class="card">
        <div class="card-title">WHO I AM</div>
        <div class="card-body">
          Hey there 👋 I’m <b>Kuki</b>, your friendly AI assistant built
          specifically for <b>USIU–Africa students</b>.
          I'm here to help you study, understand your coursework,
          and feel less stuck.
        </div>
      </div>

      <div class="card">
        <div class="card-title">WHAT I DO</div>
        <div class="card-body">
          I explain topics, summarize lectures, and clarify concepts —
          using <b>your own study material</b>.
          I'm not just guessing from the internet,
          I'm reading what you gave me.
        </div>
      </div>

      <div class="card">
        <div class="card-title">HOW I WORK</div>
        <div class="card-body">
          <div class="listish">
            <div><span class="dot">•</span>I only use the files <b>you’ve uploaded</b> — AI notes, Math PDFs, Info Literacy slides, etc.</div>
            <div><span class="dot">•</span>I pull answers, explanations, and summaries directly from those files.</div>
            <div><span class="dot">•</span>If it’s <b>not</b> in your material, I’ll tell you honestly:<br>
            “Sorry, but I can’t seem to get the answer to that right now.”</div>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="card-title">HOW TO ASK ME</div>
        <div class="card-body">
          Try:
          <div class="listish">
            <div><span class="dot">•</span>“Explain matrix inversion from my Linear Algebra notes.”</div>
            <div><span class="dot">•</span>“Summarize knowledge representation from Week 5.”</div>
            <div><span class="dot">•</span>“Differentiate between information literacy and information technology.”</div>
          </div>
          <br>
          You can also tell me the style you want:
          <div class="listish">
            <div><span class="dot">•</span><b>Short summary</b></div>
            <div><span class="dot">•</span><b>Step-by-step explanation</b></div>
            <div><span class="dot">•</span><b>Study notes format</b> (clean bullet points)</div>
          </div>
        </div>
      </div>

      <div class="card" style="grid-column: span 2; min-height: 140px;">
        <div class="card-title">YOUR NEXT STEP</div>
        <div class="card-body">
          We can dive into any topic you’ve uploaded — like
          <b>Search Algorithms</b>, <b>Differential Equations</b>,
          <b>Knowledge Representation</b>, or
          <b>Information Literacy</b>.<br><br>
          Ask me something you're revising for class.
          I’ll walk you through it.
        </div>
      </div>

    </div>
  </div>

<script>
/* STARFIELD + SHOOTING STAR */
const cvs = document.getElementById('stars');
const ctx = cvs.getContext('2d');

let stars = [];
let shootingStar = null;
let respawnCooldown = 0;

function resize() {
  cvs.width = innerWidth;
  cvs.height = innerHeight;
}
function initStars() {
  const STAR_COUNT = 420;
  stars = Array.from({length: STAR_COUNT}, () => ({
    x: Math.random() * cvs.width,
    y: Math.random() * cvs.height,
    r: 0.1 + Math.random() * 0.4,
    alpha: 0.3 + Math.random() * 0.4,
    twinkle: (Math.random() * 0.02) + 0.005
  }));
}
function handleResize() {
  resize();
  initStars();
}
addEventListener('resize', handleResize);
handleResize();

function spawnShootingStar() {
  const startX = Math.random() < 0.5
    ? Math.random() * (cvs.width * 0.25)
    : cvs.width - Math.random() * (cvs.width * 0.25);
  const startY = Math.random() * (cvs.height * 0.25);

  const speed = 9 + Math.random() * 3;
  const baseAngleDeg = Math.random() < 0.5 ? 25 : 155;
  const jitter = (Math.random() * 10) - 5;
  const angle = (baseAngleDeg + jitter) * Math.PI / 180;

  shootingStar = {
    x: startX,
    y: startY,
    vx: Math.cos(angle) * speed,
    vy: Math.sin(angle) * speed,
    life: 0,
    maxLife: 70 + Math.random() * 20,
    baseLen: 60 + Math.random() * 20
  };
}
function fadeStrength(star) {
  const t = star.life / star.maxLife;
  return (1 - t) * (1 - t);
}
function drawShootingStar(star) {
  const fade = fadeStrength(star);
  const lenNow = star.baseLen * fade;
  const vMag = Math.hypot(star.vx, star.vy) || 1;
  const tailX = star.x - star.vx * (lenNow / vMag);
  const tailY = star.y - star.vy * (lenNow / vMag);

  ctx.save();
  ctx.globalCompositeOperation = "lighter";

  const grad = ctx.createLinearGradient(star.x, star.y, tailX, tailY);
  grad.addColorStop(0, `rgba(255,255,255,${0.8 * fade})`);
  grad.addColorStop(0.25, `rgba(210,210,255,${0.4 * fade})`);
  grad.addColorStop(1, `rgba(140,120,255,0)`);

  ctx.lineWidth = 0.8;
  ctx.lineCap = "round";
  ctx.shadowBlur = 4 * fade;
  ctx.shadowColor = "rgba(200,180,255,0.6)";
  ctx.strokeStyle = grad;

  ctx.beginPath();
  ctx.moveTo(star.x, star.y);
  ctx.lineTo(tailX, tailY);
  ctx.stroke();

  ctx.shadowBlur = 6 * fade;
  ctx.fillStyle = `rgba(255,255,255,${0.9 * fade})`;
  ctx.beginPath();
  ctx.arc(star.x, star.y, 0.7, 0, Math.PI * 2);
  ctx.fill();

  ctx.restore();
}
function animate() {
  ctx.clearRect(0, 0, cvs.width, cvs.height);

  for (const s of stars) {
    s.alpha += s.twinkle * (Math.random() > 0.5 ? 1 : -1);
    s.alpha = Math.min(Math.max(s.alpha, 0.15), 0.8);
    ctx.beginPath();
    ctx.arc(s.x, s.y, s.r, 0, Math.PI * 2);
    ctx.fillStyle = `rgba(255,255,255,${s.alpha})`;
    ctx.fill();
  }

  if (shootingStar) {
    shootingStar.life += 1;
    shootingStar.x += shootingStar.vx;
    shootingStar.y += shootingStar.vy;

    drawShootingStar(shootingStar);

    const outOfBounds =
      shootingStar.x < -100 ||
      shootingStar.y < -100 ||
      shootingStar.x > cvs.width + 100 ||
      shootingStar.y > cvs.height + 100;

    if (shootingStar.life > shootingStar.maxLife || outOfBounds) {
      shootingStar = null;
      respawnCooldown = 600 + Math.floor(Math.random() * 900);
    }
  } else {
    if (respawnCooldown > 0) {
      respawnCooldown -= 1;
    } else {
      if (Math.random() < 0.003) {
        spawnShootingStar();
      }
    }
  }

  requestAnimationFrame(animate);
}
animate();

/* THEME TOGGLE */
const themeToggle = document.getElementById('themeToggle');
themeToggle.addEventListener('click', () => {
  document.body.classList.toggle('light-mode');
});

/* MENU TOGGLE + NAV */
const menuShell   = document.getElementById('menuShell');
const menuToggle  = document.getElementById('menuToggle');
const menuItemsEl = document.getElementById('menuItems');

menuToggle.addEventListener('click', () => {
  menuShell.classList.toggle('open');
});

[...menuItemsEl.querySelectorAll('.menu-item')].forEach(item => {
  item.addEventListener('click', () => {
    const target = item.getAttribute('data-link');
    if (!target) return;
    window.location.href = window.location.origin + target;
  });
});

/* PARALLAX ON TITLE */
document.addEventListener('mousemove', e => {
  const offsetX = (e.clientX / window.innerWidth - 0.5) * 20;
  const offsetY = (e.clientY / window.innerHeight - 0.5) * 20;
  document.querySelector('.about-title').style.transform =
    `translate(${offsetX}px, ${offsetY}px)`;
});
</script>

</body>
</html>
"""

# ---------------------------------------------------------
# 🎬 Render fullscreen iframe
# ---------------------------------------------------------
html(about_html, height=1000, scrolling=False)
