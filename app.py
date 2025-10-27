import streamlit as st
from streamlit.components.v1 import html

# ---------------------------------------------------------
# 🌌 Streamlit Page Config
# ---------------------------------------------------------
st.set_page_config(
    page_title="KUKI • Galaxy",
    page_icon="💜",
    layout="wide",
)

# ---------------------------------------------------------
# 🎨 Global Style Overrides (hide Streamlit UI, full-bleed background)
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
# 🚀 Page HTML (app chrome lives in here)
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
  /* Light mode orbital dawn (space + sunrise at horizon) */
  --bg-light: radial-gradient(
      circle at 50% 15%,
      #1a0f2a 0%,
      #0d0a1a 40%,
      #000008 75%,
      #000000 100%
  );

  /* Word gradient (dark mode KUKI letters) */
  --kuki-dark: linear-gradient(
    90deg,
    #c084fc 0%,
    #818cf8 35%,
    #60a5fa 60%,
    #e879f9 100%
  );

  /* Word gradient (light mode KUKI letters) */
  --kuki-light: radial-gradient(circle at 50% 20%,
    #ffd8a8 0%,
    #ff94c7 30%,
    #b28dff 60%,
    #6fb8ff 100%
  );

  /* CTA text glow base in dark */
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

  /* cinematic crossfade when toggling theme */
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
   DARK-SPACE NEBULA GLOW (fades in dark mode only)
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
   SUNRISE / HORIZON STACK (light mode reveal)
   These layers together fake that soft rim glow + reflection.
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

/* off-camera sun bloom */
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

/* ---------------------------------
   KUKI word
----------------------------------*/
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

@keyframes floatWord {
  0%, 100% { transform: translateY(0); }
  50%      { transform: translateY(-10px); }
}

/* ---------------------------------
   CTA "💬 Chat with Kuki"
   Dark mode: text itself glows in-place.
   Light mode: text floats above a soft bloom pad (not a 90s pill).
----------------------------------*/
.cta-wrap {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  pointer-events: auto;
  margin-top: 4px;
}

/* This is the bloom pad IN DARK MODE it's subtle, IN LIGHT MODE it becomes the bright sunlit pad. */
.cta-backdrop {
  position: absolute;
  left: 50%;
  top: 50%;
  transform: translate(-50%,-50%);
  min-width: 200px;
  height: 40px;
  border-radius: 9999px;
  background: radial-gradient(circle at 30% 30%, rgba(139,92,246,.18) 0%, rgba(0,0,0,0) 70%);
  box-shadow:
    0 30px 80px rgba(168,85,247,.18),
    0 0 60px rgba(99,102,241,.3);
  filter: blur(16px);
  opacity: .9;
  transition:
    all 2s ease;
}

/* Actual text line */
.cta-line {
  position: relative;
  font-size: clamp(0.9rem, 1vw, 1.05rem);
  font-weight: 600;
  line-height: 1;
  display: inline-flex;
  align-items: center;
  gap: .5rem;
  padding: .75rem 1.25rem;
  border-radius: 9999px;
  user-select: none;
  cursor: pointer;

  color: transparent;
  background: var(--cta-dark-grad);
  -webkit-background-clip: text;

  text-shadow:
    0 0 6px rgba(139,92,246,.45),
    0 0 18px rgba(99,102,241,.35),
    0 0 32px rgba(236,72,153,.25);

  filter:
    drop-shadow(0 0 6px rgba(139,92,246,.45))
    drop-shadow(0 0 18px rgba(99,102,241,.35))
    drop-shadow(0 0 32px rgba(236,72,153,.25));

  animation: pulseGlow 4s ease-in-out infinite;
  transition:
    color 2s ease,
    background 2s ease,
    text-shadow 2s ease,
    filter 2s ease;
}

@keyframes pulseGlow {
  0%,100% {
    filter:
      drop-shadow(0 0 6px rgba(139,92,246,.45))
      drop-shadow(0 0 18px rgba(99,102,241,.35))
      drop-shadow(0 0 32px rgba(236,72,153,.25));
  }
  50% {
    filter:
      drop-shadow(0 0 10px rgba(168,85,247,.8))
      drop-shadow(0 0 30px rgba(99,102,241,.55))
      drop-shadow(0 0 52px rgba(236,72,153,.45));
  }
}

/* little chat bubble icon */
.cta-icon {
  font-size: 1rem;
  line-height: 1;
  background: var(--cta-dark-grad);
  -webkit-background-clip: text;
  color: transparent;
}

/* ---------------------------------
   Tagline row (KIND • INTELLIGENT • YOURS)
----------------------------------*/
.words-row {
  position: absolute;
  top: 190px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  align-items: center;
  gap: 2rem;
  pointer-events: none;
  transition: filter 2s ease;
}

.word-chip {
  font-size: clamp(0.7rem, 0.8vw, 0.8rem);
  font-weight: 600;
  letter-spacing: 0.4rem;
  text-transform: uppercase;
  white-space: nowrap;
  user-select: none;

  background: linear-gradient(
    to right,
    rgba(255,255,255,0.95) 0%,
    rgba(214,202,255,0.9) 40%,
    rgba(180,160,255,0.8) 70%,
    rgba(255,255,255,0.95) 100%
  );
  -webkit-background-clip: text;
  color: transparent;

  text-shadow:
    0 0 8px rgba(180,160,255,0.8),
    0 0 24px rgba(120,80,255,0.5),
    0 1px 0 rgba(0,0,0,0.7),
    0 2px 2px rgba(0,0,0,0.9);

  filter:
    drop-shadow(0 0 10px rgba(160,120,255,.4))
    drop-shadow(0 0 40px rgba(100,60,255,.2));

  animation: chipFloat 6s ease-in-out infinite;
  transition: all 2s ease;
}
.word-chip:nth-child(1) { animation-delay: 0s; }
.word-chip:nth-child(2) { animation-delay: 1s; }
.word-chip:nth-child(3) { animation-delay: 2s; }

@keyframes chipFloat {
  0%,100% { transform: translateY(0) translateZ(20px) rotateX(12deg); }
  50%     { transform: translateY(-5px) translateZ(24px) rotateX(9deg); }
}

.bullet {
  font-size: clamp(0.7rem, 0.8vw, 0.8rem);
  font-weight: 400;
  color: rgba(255,255,255,0.5);
  letter-spacing: 0.4rem;
  text-shadow:
    0 0 6px rgba(200,180,255,0.6),
    0 0 20px rgba(120,80,255,0.4);
  animation: chipFloat 6s ease-in-out infinite;
  user-select: none;
  pointer-events: none;
  transition: all 2s ease;
}

/* =====================================================
   🌗 THEME TOGGLE (top-right)
===================================================== */
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
  transition:
    background 0.3s ease,
    box-shadow 0.3s ease,
    color 0.3s ease;
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
.icon-sun { display: none; }

/* =====================================================
   🚀 RETRACTABLE SPACE MENU (top-center)
   - a tiny glowing puck you tap
   - items materialize + drift down like capsules
===================================================== */

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

/* little orb toggle */
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

/* floating menu items container */
.menu-items {
  position: relative;
  width: max-content;
  margin-top: 10px;
  pointer-events: none; /* default off until open */
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

  transition:
    opacity .4s ease,
    transform .4s ease;
  cursor: pointer;
  pointer-events: auto; /* we'll toggle off/on using container's class */
}

/* positions for each word when OPEN */
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

/* when menu closed, chevron points down; open -> up */
.menu-shell.open .chevron {
  transform: rotate(180deg);
}

/* disable clicking items if closed */
.menu-shell:not(.open) .menu-items {
  pointer-events: none;
}

/* =====================================================
   ☀ LIGHT MODE OVERRIDES
===================================================== */
body.light-mode {
  background: var(--bg-light);
  color: #fff;
}

/* fade stars slightly in light mode */
body.light-mode #stars {
  opacity: 0.3;
}

/* aurora mostly fades (sunlight drowns purple fog) */
body.light-mode .aurora {
  opacity: 0.15;
}

/* sunrise layers slide up and glow */
body.light-mode .horizon-wrap {
  opacity: 1;
  bottom: -5vh;
  filter: blur(60px);
}

/* sun bloom creeps to the rim */
body.light-mode .sun-glow {
  opacity: 1;
  bottom: 0vh;
  filter: blur(70px);
}

/* KUKI text warms & gains dark rim so it's still readable */
body.light-mode .letter {
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

/* Chat CTA becomes "floating over a sunlit pad"
   - The text turns white (not clipped gradient)
   - We generate a warm bloom pad using ::before
   - The old dark-mode radial backdrop softens
*/
body.light-mode .cta-line {
  color: #fff;
  background: none;
  -webkit-background-clip: border-box;
  text-shadow:
    0 0 2px rgba(0,0,0,0.8),
    0 1px 2px rgba(0,0,0,0.9),
    0 0 8px rgba(255,255,210,.6),
    0 0 24px rgba(255,180,200,.4);
  filter:
    drop-shadow(0 0 6px rgba(255,200,150,.4))
    drop-shadow(0 0 18px rgba(255,255,200,.25))
    drop-shadow(0 0 32px rgba(255,180,240,.25));
}

body.light-mode .cta-icon {
  color:#fff;
  background:none;
  -webkit-background-clip:border-box;
  text-shadow:
    0 0 4px rgba(0,0,0,.7),
    0 0 8px rgba(255,255,210,.6),
    0 0 20px rgba(255,160,200,.4);
}

body.light-mode .cta-backdrop {
  /* morph from purple haze to warm sunrise bloom */
  min-width: 210px;
  height: 44px;
  background: radial-gradient(circle at 40% 40%,
    rgba(255,255,210,.55) 0%,
    rgba(255,190,140,.35) 30%,
    rgba(255,120,210,.18) 60%,
    rgba(0,0,0,0) 75%);
  box-shadow:
    0 30px 80px rgba(255,180,120,.18),
    0 0 60px rgba(255,160,220,.4);
  filter: blur(22px);
  opacity: .9;
}

/* tagline warms + gets slight dark rim for contrast */
body.light-mode .words-row .word-chip {
  background: linear-gradient(
    to right,
    rgba(255,235,210,0.95) 0%,
    rgba(255,200,180,0.9) 30%,
    rgba(200,160,255,0.85) 60%,
    rgba(160,180,255,0.9) 100%
  );
  -webkit-background-clip: text;
  color: transparent;
  text-shadow:
    0 0 4px rgba(0,0,0,0.7),
    0 0 12px rgba(255,220,180,0.6),
    0 0 28px rgba(255,140,200,0.35);
  filter:
    drop-shadow(0 0 10px rgba(255,200,160,.3))
    drop-shadow(0 0 30px rgba(255,120,200,.2));
}

body.light-mode .words-row .bullet {
  color: #fff;
  text-shadow:
    0 0 4px rgba(0,0,0,0.7),
    0 0 12px rgba(255,230,200,0.5),
    0 0 24px rgba(255,150,200,0.3);
}

/* theme-toggle becomes sunlit */
body.light-mode .theme-toggle {
  background: rgba(255,255,255,0.15);
  color: #fff;
  border: 1px solid rgba(255,255,255,0.3);
  box-shadow:
    0 10px 30px rgba(255,200,160,0.4),
    0 0 20px rgba(255,255,200,0.6);
}
body.light-mode .icon-moon { display: none; }
body.light-mode .icon-sun  { display: block; }

/* menu-toggle orb: warm glow in light mode */
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

/* menu items keep their floating holo vibe, so no big change needed */

/* =====================================================
   RESPONSIVE
===================================================== */
@media (max-width: 600px) {
  .orbit-area {
    min-width: 320px;
    min-height: 260px;
  }
  .words-row {
    top: 200px;
    gap: 1rem;
  }
  .word-chip,
  .bullet {
    font-size: 0.7rem;
    letter-spacing: 0.3rem;
  }
  .theme-toggle {
    top: 16px;
    right: 16px;
    font-size: 0.75rem;
    padding: 8px 12px;
  }
  .menu-shell {
    top: 16px;
  }
}
</style>
</head>
<body>

  <!-- =====================================================
       🌌 TOP FLOATING MENU
       (ABOUT links to /about — move your about.py into pages/about.py)
  ====================================================== -->
  <div class="menu-shell" id="menuShell">
    <div class="menu-toggle" id="menuToggle">
      <div class="chevron">▼</div>
    </div>
    <div class="menu-items" id="menuItems">
      <div class="menu-item" data-link="/about">ABOUT</div>
      <div class="menu-item" data-link="/labs">LABS</div>
      <div class="menu-item" data-link="/contact">CONTACT</div>
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
        <div class="cta-line">
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

<script>
/* =====================================================
   STARFIELD + SHOOTING STAR
===================================================== */
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
    r: 0.1 + Math.random() * 0.4, // micro specks
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
  // upper edge entry for streak across sky
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

  // twinkle
  for (const s of stars) {
    s.alpha += s.twinkle * (Math.random() > 0.5 ? 1 : -1);
    s.alpha = Math.min(Math.max(s.alpha, 0.15), 0.8);
    ctx.beginPath();
    ctx.arc(s.x, s.y, s.r, 0, Math.PI * 2);
    ctx.fillStyle = `rgba(255,255,255,${s.alpha})`;
    ctx.fill();
  }

  // shooting star
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
      // ~10–25s cooldown at ~60fps
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

/* =====================================================
   🌗 THEME TOGGLE
   toggles .light-mode on <body>
===================================================== */
const themeToggle = document.getElementById('themeToggle');
themeToggle.addEventListener('click', () => {
  document.body.classList.toggle('light-mode');
});

/* =====================================================
   🌠 PARALLAX ON 'KUKI'
===================================================== */
document.addEventListener('mousemove', e => {
  const offsetX = (e.clientX / window.innerWidth - 0.5) * 20;
  const offsetY = (e.clientY / window.innerHeight - 0.5) * 20;
  document.querySelector('.kuki').style.transform =
    `translate(${offsetX}px, ${offsetY}px)`;
});

/* =====================================================
   🚀 FLOATING MENU LOGIC
   - tap the orb to open/close
   - ABOUT navigates to /about
   > For navigation to actually work: put your about.py in /pages/about.py
===================================================== */
const menuShell   = document.getElementById('menuShell');
const menuToggle  = document.getElementById('menuToggle');
const menuItemsEl = document.getElementById('menuItems');

menuToggle.addEventListener('click', () => {
  menuShell.classList.toggle('open');
});

// click handling on items
[...menuItemsEl.querySelectorAll('.menu-item')].forEach(item => {
  item.addEventListener('click', () => {
    const target = item.getAttribute('data-link');
    if (!target) return;

    // naive routing: go to /about etc.
    // Streamlit multipage apps generate routes like /about
    // when you put about.py in /pages/about.py.
    window.location.href = window.location.origin + target;
  });
});
</script>

</body>
</html>
"""

# ---------------------------------------------------------
# 🎬 Render the landing page full-screen in Streamlit
# ---------------------------------------------------------
html(galaxy_html, height=1000, scrolling=False)
