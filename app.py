import streamlit as st
from streamlit.components.v1 import html

# ---------------------------------------------------------
# 🌌 Streamlit Page Config
# ---------------------------------------------------------
st.set_page_config(
    page_title="KUKI",
    page_icon="💜",
    layout="wide",
)

# ---------------------------------------------------------
# 🎨 Global Style Overrides (hide Streamlit UI chrome, full-bleed background)
# ---------------------------------------------------------
st.markdown("""
<style>
/* Hide Streamlit default header/footer/menu */
#MainMenu, header, footer {visibility:hidden;}

/* Remove Streamlit's default padding */
.block-container {
    padding: 0 !important;
    margin: 0 !important;
}

/* Force fullscreen dark radial background in host doc */
html, body, [class*="css"] {
    height:100%;
    width:100%;
    overflow:hidden !important;
    background: radial-gradient(circle at 50% 50%, #02000d, #000);
    font-family: 'Segoe UI', system-ui, -apple-system, BlinkMacSystemFont, "Inter", sans-serif;
}

/* Any iframe we render should cover full viewport */
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
# 🚀 Full App HTML (Home + About + Labs + Contact overlays)
# ---------------------------------------------------------
galaxy_html = """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
/* ---------------------------------
   THEME VARIABLES + BASE LAYOUT
----------------------------------*/
body {
  /* Dark mode deep space */
  --bg-dark: radial-gradient(circle at 50% 50%, #02000d 0%, #010008 40%, #000 70%);
  /* Light mode orbital dawn */
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

  --cta-dark-grad: radial-gradient(
    circle at 30% 30%,
    #c084fc 0%,
    #818cf8 40%,
    #60a5fa 70%,
    #e879f9 100%
  );

  margin: 0;
  padding: 0;
  overflow: hidden;
  background: var(--bg-dark);
  height: 100vh;
  width: 100vw;
  font-family: 'Segoe UI', system-ui, -apple-system, BlinkMacSystemFont, "Inter", sans-serif;
  color: #fff;

  transition:
    background 2s ease,
    color 2s ease;
  position: relative;
}

/* =====================================================
   CANVAS STARS + SHOOTING STAR
===================================================== */
canvas#stars {
  position: fixed;
  top: 0; left: 0;
  width: 100vw; height: 100vh;
  z-index: 1;
  transition: opacity 2s ease;
  opacity: 1;
  pointer-events: none;
}

/* =====================================================
   DARK-SPACE NEBULA GLOW
===================================================== */
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

/* =====================================================
   SUNRISE / HORIZON STACK (light mode)
===================================================== */
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
  transition:
    opacity 2s ease,
    bottom 2s ease,
    filter 2s ease;
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
  transition:
    opacity 2s ease,
    bottom 2s ease,
    filter 2s ease;
}

/* =====================================================
   CENTER HERO STACK
===================================================== */
.center {
  position: fixed;
  inset: 0;
  z-index: 3;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 24px;
  text-align: center;
  color: white;
  padding: 0 1rem;
}
.orbit-area {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 320px;
  min-height: 240px;
  pointer-events: none;
}
/* KUKI word */
.kuki {
  display: flex;
  gap: 0.6rem;
  filter:
    drop-shadow(0 0 10px rgba(168,85,247,.3))
    drop-shadow(0 0 22px rgba(99,102,241,.16));
  transition:
    transform .2s ease-out,
    filter 2s ease,
    text-shadow 2s ease;
  pointer-events: auto;
}
.letter {
  font-size: clamp(32px, 8vw, 72px);
  font-weight: 900;
  background: var(--kuki-dark);
  -webkit-background-clip: text;
  color: transparent;
  animation: floatWord 6s ease-in-out infinite;
  transition:
    background 2s ease,
    filter 2s ease,
    text-shadow 2s ease;
  text-shadow:
    0 0 8px rgba(168,85,247,.3),
    0 0 22px rgba(99,102,241,.16);
}
.letter:nth-child(odd) { animation-delay: 1s; }
@keyframes floatWord { 0%,100%{transform:translateY(0)} 50%{transform:translateY(-10px)} }

/* CTA */
.cta-wrap { position: relative; display: inline-flex; align-items: center; justify-content: center; pointer-events:auto; margin-top:4px; }
.cta-backdrop {
  position: absolute; left:50%; top:50%; transform:translate(-50%,-50%);
  min-width: 200px; height: 40px; border-radius:9999px;
  background: radial-gradient(circle at 30% 30%, rgba(139,92,246,.18) 0%, rgba(0,0,0,0) 70%);
  box-shadow: 0 30px 80px rgba(168,85,247,.18), 0 0 60px rgba(99,102,241,.3);
  filter: blur(16px); opacity: .9; transition: all 2s ease;
}
.cta-line{
  position:relative; font-size:clamp(.9rem,1vw,1.05rem); font-weight:600; line-height:1;
  display:inline-flex; align-items:center; gap:.5rem; padding:.75rem 1.25rem; border-radius:9999px;
  user-select:none; cursor:pointer; color:transparent; background:var(--cta-dark-grad); -webkit-background-clip:text;
  text-shadow:0 0 6px rgba(139,92,246,.45), 0 0 18px rgba(99,102,241,.35), 0 0 32px rgba(236,72,153,.25);
  filter: drop-shadow(0 0 6px rgba(139,92,246,.45)) drop-shadow(0 0 18px rgba(99,102,241,.35)) drop-shadow(0 0 32px rgba(236,72,153,.25));
  animation:pulseGlow 4s ease-in-out infinite; transition: color 2s ease, background 2s ease, text-shadow 2s ease, filter 2s ease;
}
@keyframes pulseGlow{0%,100%{filter:drop-shadow(0 0 6px rgba(139,92,246,.45)) drop-shadow(0 0 18px rgba(99,102,241,.35)) drop-shadow(0 0 32px rgba(236,72,153,.25))}50%{filter:drop-shadow(0 0 10px rgba(168,85,247,.8)) drop-shadow(0 0 30px rgba(99,102,241,.55)) drop-shadow(0 0 52px rgba(236,72,153,.45))}}
.cta-icon{font-size:1rem; line-height:1; background:var(--cta-dark-grad); -webkit-background-clip:text; color:transparent}

/* Tagline */
.words-row{position:absolute; top:190px; left:50%; transform:translateX(-50%); display:flex; align-items:center; gap:2rem; pointer-events:none; transition:filter 2s ease;}
.word-chip{font-size:clamp(.7rem,.8vw,.8rem); font-weight:600; letter-spacing:.4rem; text-transform:uppercase; white-space:nowrap; user-select:none;
  background:linear-gradient(to right, rgba(255,255,255,.95) 0%, rgba(214,202,255,.9) 40%, rgba(180,160,255,.8) 70%, rgba(255,255,255,.95) 100%); -webkit-background-clip:text; color:transparent;
  text-shadow:0 0 8px rgba(180,160,255,.8), 0 0 24px rgba(120,80,255,.5), 0 1px 0 rgba(0,0,0,.7), 0 2px 2px rgba(0,0,0,.9);
  filter:drop-shadow(0 0 10px rgba(160,120,255,.4)) drop-shadow(0 0 40px rgba(100,60,255,.2)); animation:chipFloat 6s ease-in-out infinite; transition:all 2s ease;}
.word-chip:nth-child(1){animation-delay:0s}.word-chip:nth-child(2){animation-delay:1s}.word-chip:nth-child(3){animation-delay:2s}
@keyframes chipFloat{0%,100%{transform:translateY(0) translateZ(20px) rotateX(12deg)} 50%{transform:translateY(-5px) translateZ(24px) rotateX(9deg)}}
.bullet{font-size:clamp(.7rem,.8vw,.8rem); font-weight:400; color:rgba(255,255,255,.5); letter-spacing:.4rem; text-shadow:0 0 6px rgba(200,180,255,.6), 0 0 20px rgba(120,80,255,.4); animation:chipFloat 6s ease-in-out infinite; user-select:none; pointer-events:none; transition:all 2s ease}

/* =====================================================
   🌗 THEME TOGGLE (top-right)
===================================================== */
.theme-toggle{position:fixed; top:24px; right:24px; z-index:20; background:rgba(0,0,0,.4); border:1px solid rgba(255,255,255,.15); backdrop-filter:blur(6px); box-shadow:0 10px 30px rgba(0,0,0,.6), 0 0 20px rgba(139,92,246,.4); border-radius:9999px; padding:8px 14px; font-size:.8rem; font-weight:500; color:#fff; display:flex; align-items:center; gap:8px; cursor:pointer; user-select:none; line-height:1; transition:background .3s ease, box-shadow .3s ease, color .3s ease}
.theme-toggle:hover{box-shadow:0 12px 36px rgba(0,0,0,.7), 0 0 28px rgba(236,72,153,.5), 0 0 60px rgba(99,102,241,.4)}
.icon-moon,.icon-sun{font-size:1rem; line-height:1; display:flex; align-items:center; justify-content:center}.icon-sun{display:none}

/* =====================================================
   🚀 RETRACTABLE SPACE MENU (top-center)
===================================================== */
.menu-shell{position:fixed; top:24px; left:50%; transform:translateX(-50%); z-index:20; display:flex; flex-direction:column; align-items:center; pointer-events:auto; user-select:none; color:#fff; font-size:.75rem; line-height:1.2; font-weight:500}
.menu-toggle{position:relative; width:44px; height:44px; border-radius:9999px; background:radial-gradient(circle at 30% 30%, rgba(140,120,255,.4) 0%, rgba(0,0,0,0) 70%); box-shadow:0 10px 30px rgba(0,0,0,.7), 0 0 30px rgba(140,120,255,.6), 0 0 80px rgba(255,120,200,.4); border:1px solid rgba(255,255,255,.15); backdrop-filter:blur(6px); display:flex; align-items:center; justify-content:center; cursor:pointer; color:#fff; text-shadow:0 0 4px rgba(255,255,255,.8), 0 0 12px rgba(140,120,255,.8), 0 0 40px rgba(236,72,153,.6); transition:all .3s ease}
.menu-toggle .chevron{font-size:.8rem; line-height:1; transform:translateY(0); transition:transform .3s ease}
.menu-items{position:relative; width:max-content; margin-top:10px; pointer-events:none}
.menu-item{position:absolute; left:50%; transform:translate(-50%,-10px) scale(.8); opacity:0; white-space:nowrap; letter-spacing:.15em; font-size:.7rem; font-weight:600; color:#fff; text-transform:uppercase;
  text-shadow:0 0 4px rgba(255,255,255,.9), 0 0 10px rgba(160,120,255,.6), 0 0 30px rgba(255,120,200,.4);
  filter:drop-shadow(0 0 6px rgba(160,120,255,.4)) drop-shadow(0 0 20px rgba(255,120,200,.2));
  padding:.4rem .8rem; border-radius:9999px; background:radial-gradient(circle at 30% 30%, rgba(0,0,0,.4) 0%, rgba(0,0,0,0) 70%); backdrop-filter:blur(6px);
  transition:opacity .4s ease, transform .4s ease; cursor:pointer; pointer-events:auto}
.menu-shell.open .menu-item:nth-child(1){top:50px; opacity:1; transform:translate(-50%,0) scale(1); transition-delay:.05s}
.menu-shell.open .menu-item:nth-child(2){top:90px; opacity:1; transform:translate(-50%,0) scale(1); transition-delay:.12s}
.menu-shell.open .menu-item:nth-child(3){top:130px; opacity:1; transform:translate(-50%,0) scale(1); transition-delay:.19s}
.menu-shell.open .chevron{transform:rotate(180deg)}
.menu-shell:not(.open) .menu-items{pointer-events:none}

/* =====================================================
   🪐 GLASS "SHEET" COMPONENT (used by About/Labs/Contact)
   - aura glow
   - glass card
   - custom scroll orb with moon/sun swap
===================================================== */
.sheet-aura{
  position:fixed; top:110px; left:50%; transform:translateX(-50%) scale(.95);
  width:520px; max-width:90vw; height:480px; max-height:75vh; pointer-events:none; border-radius:50%;
  background:radial-gradient(circle at 50% 30%, rgba(140,120,255,.28) 0%, rgba(40,0,80,.15) 40%, rgba(0,0,0,0) 70%);
  filter:blur(90px); mix-blend-mode:screen; opacity:0; z-index:25; transition:opacity .4s ease, filter .4s ease, transform .4s ease
}
.sheet-aura.open{opacity:1; filter:blur(110px); transform:translateX(-50%) scale(1)}

.sheet-panel{
  position:fixed; top:120px; left:50%; transform:translateX(-50%) translateY(-20px) scale(.97);
  width:min(90vw, 520px); max-width:520px; max-height:480px; padding:2.5rem 1.25rem 1rem; border-radius:1.25rem; z-index:30;
  background:radial-gradient(circle at 20% 20%, rgba(20,0,40,.55) 0%, rgba(0,0,0,.2) 70%), radial-gradient(circle at 80% 20%, rgba(140,120,255,.15) 0%, rgba(0,0,0,0) 70%);
  box-shadow:0 40px 120px rgba(0,0,0,.9), 0 0 80px rgba(140,120,255,.4), 0 0 160px rgba(255,120,200,.25);
  border:1px solid rgba(255,255,255,.22); backdrop-filter:blur(16px); color:#fff; font-size:.8rem; line-height:1.5; letter-spacing:.02em;
  text-shadow:0 0 6px rgba(255,255,255,.24), 0 0 20px rgba(140,120,255,.45);
  opacity:0; pointer-events:none; transition:opacity .4s ease, transform .4s ease
}
.sheet-panel.open{opacity:1; pointer-events:auto; transform:translateX(-50%) translateY(0) scale(1)}

.sheet-close{position:absolute; top:.75rem; right:.75rem; display:flex; z-index:50}
.sheet-close-btn{font-size:.75rem; line-height:1; cursor:pointer; color:#fff; background:radial-gradient(circle at 30% 30%, rgba(0,0,0,.6) 0%, rgba(0,0,0,0) 70%); border-radius:9999px; padding:.4rem .6rem; border:1px solid rgba(255,255,255,.25); box-shadow:0 10px 30px rgba(0,0,0,.8), 0 0 20px rgba(140,120,255,.6), 0 0 60px rgba(236,72,153,.4); text-shadow:0 0 4px rgba(255,255,255,.9), 0 0 10px rgba(160,120,255,.6), 0 0 30px rgba(255,120,200,.4)}

.scroll-orb{position:absolute; left:50%; top:0; transform:translate(-50%, -50%); width:44px; height:44px; border-radius:9999px; background:radial-gradient(circle at 30% 30%, rgba(140,120,255,.4) 0%, rgba(0,0,0,0) 70%); border:1px solid rgba(255,255,255,.2); box-shadow:0 20px 40px rgba(0,0,0,.9), 0 0 30px rgba(140,120,255,.7), 0 0 80px rgba(255,120,200,.4); display:flex; align-items:center; justify-content:center; font-size:.9rem; color:#fff; text-shadow:0 0 4px rgba(255,255,255,.8), 0 0 12px rgba(140,120,255,.8), 0 0 40px rgba(236,72,153,.6); pointer-events:none; transition:background .4s ease, box-shadow .4s ease, border .4s ease, color .4s ease, text-shadow .4s ease}
.scroll-orb .orb-icon{transition:all .3s ease}
.scroll-orb.day{background:radial-gradient(circle at 30% 30%, rgba(255,230,170,.45) 0%, rgba(0,0,0,0) 70%); border:1px solid rgba(255,255,255,.4); box-shadow:0 20px 40px rgba(0,0,0,.6), 0 0 30px rgba(255,200,150,.7), 0 0 80px rgba(255,255,210,.5); text-shadow:0 0 4px rgba(0,0,0,.8), 0 0 12px rgba(255,220,160,.8)}

.sheet-headline{font-size:.8rem; font-weight:600; letter-spacing:.15em; text-transform:uppercase; margin-bottom:.75rem; background:linear-gradient(90deg,#c084fc 0%,#818cf8 35%,#60a5fa 60%,#e879f9 100%); -webkit-background-clip:text; color:transparent; text-shadow:0 0 8px rgba(180,160,255,.8), 0 0 24px rgba(120,80,255,.5), 0 1px 0 rgba(0,0,0,.7), 0 2px 2px rgba(0,0,0,.9)}

.sheet-scroll{position:relative; max-height:320px; overflow-y:auto; padding-right:.5rem; scrollbar-width:none}
.sheet-scroll::-webkit-scrollbar{display:none}

.sheet-body p{margin:0 0 .75rem 0; font-size:.8rem; line-height:1.5}
.sheet-body strong{font-weight:600; color:#fff; text-shadow:0 0 6px rgba(255,255,255,.5), 0 0 24px rgba(140,120,255,.6)}
.section-label{font-size:.7rem; font-weight:600; letter-spacing:.12em; text-transform:uppercase; opacity:.8; margin:1rem 0 .4rem 0; color:#fff; text-shadow:0 0 4px rgba(255,255,255,.4), 0 0 16px rgba(140,120,255,.5)}
.sheet-list{margin:0 0 .75rem 0; padding-left:1rem; list-style:none}
.sheet-list li{position:relative; padding-left:1rem; margin:0 0 .5rem 0; font-size:.8rem; line-height:1.5}
.sheet-list li::before{content:"✦"; position:absolute; left:0; top:0; font-size:.6rem; line-height:1.4; color:#fff; text-shadow:0 0 6px rgba(255,255,255,.8), 0 0 20px rgba(140,120,255,.8), 0 0 40px rgba(236,72,153,.6)}

.tip-box{border-radius:.75rem; padding:.75rem .75rem; background:radial-gradient(circle at 20% 20%, rgba(255,255,255,.07) 0%, rgba(0,0,0,0) 70%); border:1px solid rgba(255,255,255,.2); box-shadow:0 20px 60px rgba(0,0,0,.8), 0 0 40px rgba(140,120,255,.4), 0 0 80px rgba(255,120,200,.2); text-shadow:0 0 6px rgba(255,255,255,.4), 0 0 20px rgba(140,120,255,.5); margin-top:.75rem; font-size:.75rem; line-height:1.5}

/* Simple pill links inside sheets */
.sheet-link{display:inline-flex; align-items:center; gap:.5rem; padding:.5rem .8rem; border-radius:9999px; border:1px solid rgba(255,255,255,.25); backdrop-filter:blur(6px); background:radial-gradient(circle at 30% 30%, rgba(0,0,0,.45) 0%, rgba(0,0,0,0) 70%); text-decoration:none; color:#fff; font-size:.78rem; box-shadow:0 10px 30px rgba(0,0,0,.7), 0 0 24px rgba(140,120,255,.5); text-shadow:0 0 6px rgba(255,255,255,.7)}
.sheet-link:hover{box-shadow:0 12px 36px rgba(0,0,0,.75), 0 0 34px rgba(236,72,153,.5)}

/* =====================================================
   ☀ LIGHT MODE OVERRIDES
===================================================== */
body.light-mode { background: var(--bg-light); color:#fff }
body.light-mode #stars{opacity:.3} body.light-mode .aurora{opacity:.15}
body.light-mode .horizon-wrap{opacity:1; bottom:-5vh; filter:blur(60px)}
body.light-mode .sun-glow{opacity:1; bottom:0vh; filter:blur(70px)}

body.light-mode .letter{background:var(--kuki-light); -webkit-background-clip:text; color:transparent;
  filter:drop-shadow(0 0 4px rgba(255,200,160,.4)) drop-shadow(0 0 12px rgba(255,255,200,.25));
  text-shadow:0 0 2px rgba(0,0,0,.6), 0 1px 2px rgba(0,0,0,.8), 0 0 8px rgba(255,200,160,.35), 0 0 22px rgba(255,255,200,.2)}
body.light-mode .cta-line{color:#fff; background:none; -webkit-background-clip:border-box; text-shadow:0 0 2px rgba(0,0,0,.8), 0 1px 2px rgba(0,0,0,.9), 0 0 8px rgba(255,255,210,.6), 0 0 24px rgba(255,180,200,.4);
  filter:drop-shadow(0 0 6px rgba(255,200,150,.4)) drop-shadow(0 0 18px rgba(255,255,200,.25)) drop-shadow(0 0 32px rgba(255,180,240,.25))}
body.light-mode .cta-icon{color:#fff; background:none; -webkit-background-clip:border-box; text-shadow:0 0 4px rgba(0,0,0,.7), 0 0 8px rgba(255,255,210,.6), 0 0 20px rgba(255,160,200,.4)}
body.light-mode .cta-backdrop{min-width:210px; height:44px; background:radial-gradient(circle at 40% 40%, rgba(255,255,210,.55) 0%, rgba(255,190,140,.35) 30%, rgba(255,120,210,.18) 60%, rgba(0,0,0,0) 75%);
  box-shadow:0 30px 80px rgba(255,180,120,.18), 0 0 60px rgba(255,160,220,.4); filter:blur(22px); opacity:.9}
body.light-mode .words-row .word-chip{background:linear-gradient(to right, rgba(255,235,210,.95) 0%, rgba(255,200,180,.9) 30%, rgba(200,160,255,.85) 60%, rgba(160,180,255,.9) 100%); -webkit-background-clip:text; color:transparent;
  text-shadow:0 0 4px rgba(0,0,0,.7), 0 0 12px rgba(255,220,180,.6), 0 0 28px rgba(255,140,200,.35);
  filter:drop-shadow(0 0 10px rgba(255,200,160,.3)) drop-shadow(0 0 30px rgba(255,120,200,.2))}
body.light-mode .words-row .bullet{color:#fff; text-shadow:0 0 4px rgba(0,0,0,.7), 0 0 12px rgba(255,230,200,.5), 0 0 24px rgba(255,150,200,.3)}

body.light-mode .theme-toggle{background:rgba(255,255,255,.15); color:#fff; border:1px solid rgba(255,255,255,.3); box-shadow:0 10px 30px rgba(255,200,160,.4), 0 0 20px rgba(255,255,200,.6)}
body.light-mode .icon-moon{display:none} body.light-mode .icon-sun{display:block}
body.light-mode .menu-toggle{background:radial-gradient(circle at 30% 30%, rgba(255,230,170,.4) 0%, rgba(0,0,0,0) 70%); box-shadow:0 10px 30px rgba(0,0,0,.6), 0 0 30px rgba(255,200,150,.6), 0 0 80px rgba(255,255,210,.4); border:1px solid rgba(255,255,255,.4); text-shadow:0 0 4px rgba(0,0,0,.8), 0 0 12px rgba(255,220,160,.8), 0 0 40px rgba(255,150,200,.6)}

body.light-mode .sheet-panel{background:radial-gradient(circle at 20% 20%, rgba(60,20,0,.5) 0%, rgba(0,0,0,.15) 70%), radial-gradient(circle at 80% 20%, rgba(255,200,150,.18) 0%, rgba(0,0,0,0) 70%);
  box-shadow:0 40px 120px rgba(0,0,0,.7), 0 0 80px rgba(255,200,150,.4), 0 0 160px rgba(255,160,200,.25); border:1px solid rgba(255,255,255,.35);
  text-shadow:0 0 6px rgba(255,240,200,.4), 0 0 20px rgba(255,200,150,.4), 0 0 40px rgba(255,140,200,.3)}
body.light-mode .sheet-close-btn{background:radial-gradient(circle at 30% 30%, rgba(0,0,0,.4) 0%, rgba(0,0,0,0) 70%); border:1px solid rgba(255,255,255,.4); box-shadow:0 10px 30px rgba(0,0,0,.7), 0 0 20px rgba(255,200,150,.6), 0 0 60px rgba(255,160,200,.4); text-shadow:0 0 4px rgba(255,255,255,.9), 0 0 10px rgba(255,200,150,.6), 0 0 30px rgba(255,160,200,.4)}
body.light-mode .sheet-aura{background:radial-gradient(circle at 50% 30%, rgba(255,210,150,.28) 0%, rgba(120,40,0,.15) 40%, rgba(0,0,0,0) 70%); box-shadow:0 0 80px rgba(255,210,150,.3), 0 0 160px rgba(255,140,200,.2)}

/* =====================================================
   RESPONSIVE
===================================================== */
@media (max-width: 600px){
  .orbit-area{min-width:320px; min-height:260px}
  .words-row{top:200px; gap:1rem}
  .word-chip,.bullet{font-size:.7rem; letter-spacing:.3rem}
  .theme-toggle{top:16px; right:16px; font-size:.75rem; padding:8px 12px}
  .menu-shell{top:16px}
  .sheet-aura{top:100px; width:90vw; height:440px; max-height:70vh}
  .sheet-panel{top:110px; width:min(92vw,520px); max-height:440px}
  .sheet-scroll{max-height:300px}
}
</style>
</head>
<body>

  <!-- =====================================================
       🌌 TOP FLOATING MENU
  ====================================================== -->
  <div class="menu-shell" id="menuShell">
    <div class="menu-toggle" id="menuToggle">
      <div class="chevron">▼</div>
    </div>
    <div class="menu-items" id="menuItems">
      <div class="menu-item" data-action="about">ABOUT</div>
      <div class="menu-item" data-action="labs">LABS</div>
      <div class="menu-item" data-action="contact">CONTACT</div>
    </div>
  </div>

  <!-- =====================================================
       🌗 THEME TOGGLE
  ====================================================== -->
  <div class="theme-toggle" id="themeToggle">
    <div class="icon-moon">🌙</div>
    <div class="icon-sun">☀️</div>
    <div class="label">mode</div>
  </div>

  <!-- stars + sunrise + nebula layers -->
  <canvas id="stars"></canvas>

  <div class="horizon-wrap">
    <div class="horizon-ring"></div>
    <div class="horizon-haze"></div>
    <div class="horizon-reflect"></div>
    <div class="horizon-sweep"></div>
  </div>

  <div class="sun-glow"></div>
  <div class="aurora"></div>

  <!-- =====================================================
       HERO CONTENT
  ====================================================== -->
  <div class="center">
    <div class="orbit-area">
      <div class="kuki">
        <span class="letter">K</span>
        <span class="letter">U</span>
        <span class="letter">K</span>
        <span class="letter">I</span>
      </div>

      <div class="cta-wrap">
        <div class="cta-backdrop"></div>
        <div class="cta-line" id="chatCTA">
          <span class="cta-icon">💬</span>
          <span>Chat with Kuki</span>
        </div>
      </div>

      <div class="words-row">
        <div class="word-chip">KIND</div>
        <div class="bullet">•</div>
        <div class="word-chip">INTELLIGENT</div>
        <div class="bullet">•</div>
        <div class="word-chip">YOURS</div>
      </div>
    </div>
  </div>

  <!-- =====================================================
       ABOUT OVERLAY
  ====================================================== -->
  <div class="sheet-aura" id="aboutAura"></div>
  <div class="sheet-panel" id="aboutPanel">
    <div class="scroll-orb" id="aboutOrb"><div class="orb-icon">🌙</div></div>
    <div class="sheet-close"><div class="sheet-close-btn" data-close="about">✕ Close</div></div>
    <div class="sheet-headline">ABOUT KUKI</div>
    <div class="sheet-scroll" id="aboutScroll">
      <div class="sheet-body">
        <p>Hey there! <strong>😊</strong></p>
        <p>I’m <strong>Kuki</strong>, your friendly AI assistant made for <strong>USIU–Africa students</strong>. I help with coursework, notes, and academic guidance — calmly, clearly, and without judgment.</p>

        <div class="section-label">WHAT I DO</div>
        <p>I help you understand topics, summarize lecture material, and explain concepts from <strong>your own course files</strong> — like your AI, Math, and Information Literacy notes.</p>

        <div class="section-label">HOW I WORK</div>
        <ul class="sheet-list">
          <li>I only use files <strong>you upload</strong> (PDFs, slides, notes).</li>
          <li>I can summarize, explain, extract definitions, compare concepts.</li>
          <li>If it's not in your files, I’ll tell you: <em>“Sorry, but I can’t seem to get the answer to that right now.”</em></li>
        </ul>

    

        <div class="section-label">STYLE</div>
        <p>Would you like answers in a <strong>summary</strong>, a <strong>step-by-step explanation</strong>, or a <strong>study-notes format</strong>?</p>

        <div class="tip-box">🔍 Tip: Start with something you're studying now — e.g. <strong>“Help me revise Search Algorithms from my notes.”</strong></div>
      </div>
    </div>
  </div>

  <!-- =====================================================
       LABS OVERLAY
  ====================================================== -->
  <div class="sheet-aura" id="labsAura"></div>
  <div class="sheet-panel" id="labsPanel">
    <div class="scroll-orb" id="labsOrb"><div class="orb-icon">🌙</div></div>
    <div class="sheet-close"><div class="sheet-close-btn" data-close="labs">✕ Close</div></div>
    <div class="sheet-headline">KUKI LABS</div>
    <div class="sheet-scroll" id="labsScroll">
      <div class="sheet-body">
        <p><strong>Kuki Labs</strong> is where new tools land first — experimental features designed for USIU–Africa coursework. Everything runs on your uploaded files; no outside web guessing.</p>

        <div class="section-label">CURRENT EXPERIMENTS</div>
        <ul class="sheet-list">
          <li><strong>Note Summarizer</strong> — distill long PDFs/PowerPoints into clean study briefs.</li>
          <li><strong>Concept Explorer</strong> — jump between linked ideas across your notes.</li>
          <li><strong>Quiz & Flashcards (beta)</strong> — generate MCQs & spaced-repetition cards from your files.</li>
          <li><strong>Study Plan Builder</strong> — turn a syllabus into a weekly plan with milestones.</li>
          <li><strong>Math From Notes</strong> — step-wise derivations using only material you provided.</li>
          <li><strong>Glossary Maker</strong> — auto-collect definitions with citations to your pages.</li>
        </ul>

        <div class="section-label">COMING SOON</div>
        <ul class="sheet-list">
          <li><strong>Source Viewer</strong> — side-by-side answers + exact page snippets.</li>
          <li><strong>Project Workspace</strong> — keep datasets, drafts, and references per course.</li>
          <li><strong>Progress Tracker</strong> — visualize what you’ve revised vs. what’s left.</li>
        </ul>

        <div class="section-label">FUTURE ROADMAP</div>
        <ul class="sheet-list">
          <li><strong>Offline Mode</strong> — on-device retrieval (RAG) so Kuki works without internet using your local notes.</li>
          <li><strong>WhatsApp Integration</strong> — chat with Kuki via WhatsApp (Twilio / WhatsApp Cloud API), with secure file linking.</li>
          <li><strong>Voice & Dictation</strong> — talk to Kuki, get spoken responses; auto-transcribe lectures to notes & flashcards.</li>
          <li><strong>Image/Diagram Tutor</strong> — point at a diagram/equation → step-by-step explanations and labels.</li>
          <li><strong>Auto Timecodes for Lectures</strong> — paste a video/recording → get chapter timecodes + question-cards.</li>
          <li><strong>Lab Data Assistant</strong> — CSV/Excel helper for cleaning, plots, quick stats, and APA-style tables.</li>
          <li><strong>Team Study Rooms</strong> — shared space per course (files, tasks, comments) with role permissions.</li>
          <li><strong>Strict Citation Mode</strong> — every answer with page/slide anchors back to your uploaded files.</li>
          <li><strong>Privacy Controls</strong> — per-file retention, redaction, and “never store” toggles.</li>
          <li><strong>Admin Console</strong> — course templates, usage analytics, model/version toggles, and access policies.</li>
        </ul>

      

        <div class="tip-box">
          🔬 Want early access to new experiments? Use the <a class="sheet-link" id="labsJoin" href="https://chatgpt.com/g/g-6887621fc0ac8191933b2bcfba73a075-kuki" role="button">Request Labs Access</a> and mention your course.
        </div>
      </div>
    </div>
  </div>

  <!-- =====================================================
       CONTACT OVERLAY
  ====================================================== -->
  <div class="sheet-aura" id="contactAura"></div>
  <div class="sheet-panel" id="contactPanel">
    <div class="scroll-orb" id="contactOrb"><div class="orb-icon">🌙</div></div>
    <div class="sheet-close"><div class="sheet-close-btn" data-close="contact">✕ Close</div></div>
    <div class="sheet-headline">CONTACT</div>
    <div class="sheet-scroll" id="contactScroll">
      <div class="sheet-body">
        <p>Have feedback, a bug, or a feature idea for Kuki?</p>

        <div class="section-label">REACH OUT</div>
        <ul class="sheet-list">
          <li><a class="sheet-link" id="contactEmail" href="#">Email Kuki Team</a> — share your course & files context.</li>
          <li><a class="sheet-link" id="contactSupport" href="#">Report an Issue</a> — tell us what broke & attach a sample file.</li>
        </ul>

        <div class="section-label">BEST PRACTICES</div>
        <ul class="sheet-list">
          <li>Include course code, topic, and short goal (e.g., “Need flashcards for Week 7”).</li>
          <li>Strip personal info from documents before sharing.</li>
        </ul>

        <div class="tip-box">💡 Pro tip: If you want help <em>right now</em>, click “Chat with Kuki” on the home screen and paste your question — Kuki will answer using your uploaded notes.</div>
      </div>
    </div>
  </div>

<script>
/* =====================================================
   CONFIG
===================================================== */
const KUKI_AGENT_URL = "https://chatgpt.com/g/g-6887621fc0ac8191933b2bcfba73a075-kuki";
const CONTACT_EMAIL   = "chweyamark@gmail.com";     // ← updated
const REPORT_URL      = "mailto:chweyamark@gmail.com?subject=Kuki%20Issue%20Report"; // ← updated

/* =====================================================
   STARFIELD + SHOOTING STAR
===================================================== */
const cvs = document.getElementById('stars');
const ctx = cvs.getContext('2d');

let stars = [];
let shootingStar = null;
let respawnCooldown = 0;

function resize(){ cvs.width = innerWidth; cvs.height = innerHeight; }
function initStars(){
  const STAR_COUNT = 420;
  stars = Array.from({length: STAR_COUNT}, () => ({
    x: Math.random()*cvs.width,
    y: Math.random()*cvs.height,
    r: 0.1 + Math.random()*0.4,
    alpha: 0.3 + Math.random()*0.4,
    twinkle: (Math.random()*0.02) + 0.005
  }));
}
function handleResize(){ resize(); initStars(); }
addEventListener('resize', handleResize); handleResize();

function spawnShootingStar(){
  const startX = Math.random()<0.5 ? Math.random()*(cvs.width*0.25) : cvs.width - Math.random()*(cvs.width*0.25);
  const startY = Math.random()*(cvs.height*0.25);
  const speed = 9 + Math.random()*3;
  const baseAngleDeg = Math.random()<0.5 ? 25 : 155;
  const jitter = (Math.random()*10) - 5;
  const angle = (baseAngleDeg + jitter) * Math.PI/180;
  shootingStar = { x:startX, y:startY, vx:Math.cos(angle)*speed, vy:Math.sin(angle)*speed, life:0, maxLife:70+Math.random()*20, baseLen:60+Math.random()*20 };
}
function fadeStrength(star){ const t = star.life/star.maxLife; return (1-t)*(1-t); }
function drawShootingStar(star){
  const fade = fadeStrength(star);
  const lenNow = star.baseLen * fade;
  const vMag = Math.hypot(star.vx, star.vy) || 1;
  const tailX = star.x - star.vx*(lenNow/vMag);
  const tailY = star.y - star.vy*(lenNow/vMag);
  ctx.save(); ctx.globalCompositeOperation = "lighter";
  const grad = ctx.createLinearGradient(star.x, star.y, tailX, tailY);
  grad.addColorStop(0, "rgba(255,255,255,"+(0.8*fade)+")");
  grad.addColorStop(0.25, "rgba(210,210,255,"+(0.4*fade)+")");
  grad.addColorStop(1, "rgba(140,120,255,0)");
  ctx.lineWidth=0.8; ctx.lineCap="round"; ctx.shadowBlur=4*fade; ctx.shadowColor="rgba(200,180,255,0.6)"; ctx.strokeStyle=grad;
  ctx.beginPath(); ctx.moveTo(star.x, star.y); ctx.lineTo(tailX, tailY); ctx.stroke();
  ctx.shadowBlur=6*fade; ctx.fillStyle="rgba(255,255,255,"+(0.9*fade)+")"; ctx.beginPath(); ctx.arc(star.x, star.y, 0.7, 0, Math.PI*2); ctx.fill();
  ctx.restore();
}
function animate(){
  ctx.clearRect(0,0,cvs.width,cvs.height);
  for(const s of stars){
    s.alpha += s.twinkle * (Math.random()>0.5?1:-1);
    s.alpha = Math.min(Math.max(s.alpha, 0.15), 0.8);
    ctx.beginPath(); ctx.arc(s.x, s.y, s.r, 0, Math.PI*2);
    ctx.fillStyle = "rgba(255,255,255,"+s.alpha+")"; ctx.fill();
  }
  if(shootingStar){
    shootingStar.life += 1; shootingStar.x += shootingStar.vx; shootingStar.y += shootingStar.vy; drawShootingStar(shootingStar);
    const OOB = shootingStar.x<-100 || shootingStar.y<-100 || shootingStar.x>cvs.width+100 || shootingStar.y>cvs.height+100;
    if(shootingStar.life>shootingStar.maxLife || OOB){ shootingStar=null; respawnCooldown = 600 + Math.floor(Math.random()*900); }
  }else{
    if(respawnCooldown>0){ respawnCooldown -= 1; } else if(Math.random()<0.003){ spawnShootingStar(); }
  }
  requestAnimationFrame(animate);
}
animate();

/* =====================================================
   🌗 THEME TOGGLE
===================================================== */
const themeToggle = document.getElementById('themeToggle');
themeToggle.addEventListener('click', () => { document.body.classList.toggle('light-mode'); });

/* =====================================================
   🌠 PARALLAX ON 'KUKI'
===================================================== */
document.addEventListener('mousemove', e => {
  const offsetX = (e.clientX / window.innerWidth - 0.5) * 20;
  const offsetY = (e.clientY / window.innerHeight - 0.5) * 20;
  const kuki = document.querySelector('.kuki');
  if (kuki) kuki.style.transform = "translate(" + offsetX + "px," + offsetY + "px)";
});

/* =====================================================
   CTA -> Open KUKI agent
===================================================== */
const chatCTA = document.getElementById('chatCTA');
chatCTA.addEventListener('click', () => {
  window.open(KUKI_AGENT_URL, '_blank', 'noopener');
});

/* =====================================================
   FLOATING MENU & SHEETS (About/Labs/Contact)
===================================================== */
const menuShell  = document.getElementById('menuShell');
const menuToggle = document.getElementById('menuToggle');
const menuItems  = document.getElementById('menuItems');

const sheets = {
  about:   { panel: document.getElementById('aboutPanel'),   aura: document.getElementById('aboutAura'),   scroll: document.getElementById('aboutScroll'),   orb: document.getElementById('aboutOrb')   },
  labs:    { panel: document.getElementById('labsPanel'),    aura: document.getElementById('labsAura'),    scroll: document.getElementById('labsScroll'),    orb: document.getElementById('labsOrb')    },
  contact: { panel: document.getElementById('contactPanel'), aura: document.getElementById('contactAura'), scroll: document.getElementById('contactScroll'), orb: document.getElementById('contactOrb') },
};

menuToggle.addEventListener('click', () => { menuShell.classList.toggle('open'); });

// open selected sheet
[...menuItems.querySelectorAll('.menu-item')].forEach(item => {
  item.addEventListener('click', () => {
    const action = item.getAttribute('data-action');
    openSheet(action);
    menuShell.classList.remove('open');
  });
});

function openSheet(name){
  const s = sheets[name]; if (!s) return;
  s.panel.classList.add('open'); s.aura.classList.add('open');
  s.scroll.scrollTop = 0; // reset
  s.orb.classList.remove('day'); s.orb.querySelector('.orb-icon').textContent = '🌙';
  s.orb.style.transform = 'translate(-50%, -50%)';
}
// close buttons
[...document.querySelectorAll('.sheet-close-btn')].forEach(btn => {
  btn.addEventListener('click', () => {
    const name = btn.getAttribute('data-close');
    const s = sheets[name]; if (!s) return;
    s.panel.classList.remove('open'); s.aura.classList.remove('open');
  });
});

/* scroll-orb progress + sun/moon per sheet */
Object.values(sheets).forEach(s => {
  s.scroll.addEventListener('scroll', () => {
    const max = s.scroll.scrollHeight - s.scroll.clientHeight;
    const ratio = max === 0 ? 0 : s.scroll.scrollTop / max;
    const travel = ratio * 40; // ~40px travel
    s.orb.style.transform = 'translate(-50%, calc(-50% + ' + travel + 'px))';
    if (ratio > 0.5) { s.orb.classList.add('day'); s.orb.querySelector('.orb-icon').textContent = '☀️'; }
    else { s.orb.classList.remove('day'); s.orb.querySelector('.orb-icon').textContent = '🌙'; }
  });
});

/* Labs + Contact links */
const labsJoin = document.getElementById('labsJoin');
if (labsJoin) labsJoin.addEventListener('click', (e) => {
  e.preventDefault();
  window.location.href = "mailto:" + CONTACT_EMAIL + "?subject=Kuki%20Labs%20Access&body=Course(s)%3A%20%0D%0AUse-case%3A%20%0D%0AFiles%20you%27ll%20share%3A%20";
});
const contactEmail = document.getElementById('contactEmail');
if (contactEmail) contactEmail.addEventListener('click', (e)=>{ e.preventDefault(); window.location.href = "mailto:" + CONTACT_EMAIL + "?subject=Hello%20Kuki"; });
const contactSupport = document.getElementById('contactSupport');
if (contactSupport) contactSupport.addEventListener('click', (e)=>{ e.preventDefault(); window.location.href = REPORT_URL; });
</script>

</body>
</html>
"""

# ---------------------------------------------------------
# 🎬 Render the full experience in Streamlit
# ---------------------------------------------------------
html(galaxy_html, height=1000, scrolling=False)
