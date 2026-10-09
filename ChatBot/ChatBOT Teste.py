import streamlit as st
import streamlit.components.v1 as components
import anthropic
import json
from datetime import date, datetime
from pathlib import Path
from uuid import uuid4

st.set_page_config(
    page_title="🎰 BetBot AI",
    page_icon="🎰",
    layout="centered",
)

# --- CSS: black/neon futuristic theme ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@400;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Rajdhani', sans-serif !important;
        letter-spacing: 0.3px;
    }

    .stApp {
        background:
            radial-gradient(ellipse 900px 320px at 50% 0%, rgba(0,255,136,0.07), transparent 70%),
            #000000 !important;
    }

    @keyframes fadeSlideIn {
        from { opacity: 0; transform: translateY(10px); }
        to   { opacity: 1; transform: translateY(0); }
    }

    @keyframes btnPulse {
        0%, 100% { box-shadow: 0 0 10px rgba(0,255,136,0.2); }
        50%      { box-shadow: 0 0 20px rgba(0,255,136,0.45); }
    }

    /* Tabs */
    [data-testid="stTabs"] button {
        font-family: 'Orbitron', monospace !important;
        font-size: 0.75rem !important;
        font-weight: 700 !important;
        letter-spacing: 2px !important;
        color: #7fff7f !important;
        text-transform: uppercase;
    }
    [data-testid="stTabs"] button[aria-selected="true"] {
        color: #00ff88 !important;
        border-bottom: 2px solid #00ff88 !important;
        text-shadow: 0 0 8px #00ff88;
    }

    /* Chat messages */
    .user-msg {
        background: rgba(245,197,24,0.08);
        border-left: 3px solid #f5c518;
        border-radius: 0 10px 10px 0;
        padding: 0.75rem 1rem;
        margin: 0.5rem 0;
        color: #f0f0f0;
        box-shadow: 0 0 12px rgba(245,197,24,0.08);
        animation: fadeSlideIn 0.4s ease-out;
    }

    .bot-msg {
        background: rgba(0,255,136,0.05);
        border-left: 3px solid #00ff88;
        border-radius: 0 10px 10px 0;
        padding: 0.75rem 1rem;
        margin: 0.5rem 0;
        color: #d0f0d0;
        box-shadow: 0 0 12px rgba(0,255,136,0.07);
        animation: fadeSlideIn 0.4s ease-out;
    }

    .msg-label {
        font-family: 'Orbitron', monospace;
        font-size: 0.6rem;
        font-weight: 700;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-bottom: 6px;
    }

    .user-label { color: #f5c518; text-shadow: 0 0 6px rgba(245,197,24,0.6); }
    .bot-label  { color: #00ff88; text-shadow: 0 0 6px rgba(0,255,136,0.6); }

    /* Input */
    .stTextInput > div > div > input {
        background: rgba(0,255,136,0.04) !important;
        color: #e0ffe0 !important;
        border: 1px solid rgba(0,255,136,0.3) !important;
        border-radius: 6px !important;
        font-family: 'Rajdhani', sans-serif !important;
        font-size: 1rem !important;
    }
    .stTextInput > div > div > input::placeholder { color: rgba(0,255,136,0.35) !important; }
    .stTextInput > div > div > input:focus {
        border-color: #00ff88 !important;
        box-shadow: 0 0 12px rgba(0,255,136,0.25) !important;
    }

    /* Number input */
    .stNumberInput input {
        background: rgba(0,255,136,0.04) !important;
        color: #e0ffe0 !important;
        border: 1px solid rgba(0,255,136,0.3) !important;
        border-radius: 6px !important;
        font-family: 'Rajdhani', sans-serif !important;
    }

    /* Button */
    .stButton > button {
        background: transparent !important;
        color: #00ff88 !important;
        font-family: 'Orbitron', monospace !important;
        font-size: 0.7rem !important;
        font-weight: 700 !important;
        letter-spacing: 2px !important;
        border: 1px solid #00ff88 !important;
        border-radius: 6px !important;
        padding: 0.5rem 1.4rem !important;
        text-transform: uppercase;
        box-shadow: 0 0 10px rgba(0,255,136,0.2);
        transition: all 0.15s ease;
        animation: btnPulse 2.8s ease-in-out infinite;
    }
    .stButton > button:hover {
        background: rgba(0,255,136,0.12) !important;
        box-shadow: 0 0 20px rgba(0,255,136,0.4) !important;
        color: #ffffff !important;
    }

    /* Form submit button */
    [data-testid="stFormSubmitButton"] button {
        background: rgba(0,255,136,0.1) !important;
        color: #00ff88 !important;
        font-family: 'Orbitron', monospace !important;
        font-size: 0.65rem !important;
        letter-spacing: 1.5px !important;
        border: 1px solid #00ff88 !important;
        box-shadow: 0 0 12px rgba(0,255,136,0.25) !important;
    }
    [data-testid="stFormSubmitButton"] button:hover {
        background: rgba(0,255,136,0.22) !important;
        box-shadow: 0 0 24px rgba(0,255,136,0.5) !important;
    }

    /* Metrics */
    [data-testid="stMetric"] label {
        font-family: 'Orbitron', monospace !important;
        font-size: 0.6rem !important;
        letter-spacing: 1.5px !important;
        color: #7fff7f !important;
        text-transform: uppercase;
    }
    [data-testid="stMetric"] [data-testid="stMetricValue"] {
        font-family: 'Orbitron', monospace !important;
        color: #00ff88 !important;
        text-shadow: 0 0 8px rgba(0,255,136,0.4);
    }

    /* Divider */
    hr { border-color: rgba(0,255,136,0.1) !important; }

    /* Selectbox / multiselect */
    .stSelectbox label, .stMultiSelect label, .stNumberInput label, .stTextInput label {
        font-family: 'Rajdhani', sans-serif !important;
        color: #7fff7f !important;
        font-weight: 600;
    }

    /* Info box */
    [data-testid="stNotification"], .stAlert {
        background: rgba(0,255,136,0.05) !important;
        border: 1px solid rgba(0,255,136,0.2) !important;
        color: #b0ffb0 !important;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: #050505 !important;
        border-right: 1px solid rgba(0,255,136,0.1) !important;
    }
    section[data-testid="stSidebar"] * {
        color: #c0e8c0 !important;
    }
    section[data-testid="stSidebar"] h2, section[data-testid="stSidebar"] h3 {
        font-family: 'Orbitron', monospace !important;
        color: #00ff88 !important;
        text-shadow: 0 0 8px rgba(0,255,136,0.4);
        font-size: 0.85rem !important;
    }

    /* Markdown section headers */
    [data-testid="stMarkdownContainer"] h3, [data-testid="stMarkdownContainer"] h4 {
        font-family: 'Orbitron', monospace !important;
        color: #00ff88 !important;
        text-shadow: 0 0 8px rgba(0,255,136,0.35);
        letter-spacing: 1px;
        border-bottom: 1px solid rgba(0,255,136,0.25);
        padding-bottom: 6px;
    }

    /* Tab highlight underline */
    [data-testid="stTabs"] button { transition: color 0.2s ease, text-shadow 0.2s ease; }
    [data-baseweb="tab-highlight"] {
        background: linear-gradient(90deg, #00ff88, #00cfff) !important;
        box-shadow: 0 0 10px rgba(0,255,136,0.6);
    }
</style>
""", unsafe_allow_html=True)

# --- Fixed full-width top banner: football-pitch particle bar (injected at page top) ---
components.html("""
<!DOCTYPE html>
<html>
<head>
<style>html, body { margin:0; padding:0; background:transparent; overflow:hidden; }</style>
</head>
<body>
<script>
(function () {
  var BAR_ID = 'betbot-fixed-topbar';
  var STYLE_ID = 'betbot-fixed-topbar-style';
  var BAR_HEIGHT = 252;
  var TURF_HEIGHT = 96;

  function renderInto(doc, isFixed) {
    var bar = doc.createElement('div');
    bar.id = BAR_ID;
    if (isFixed) {
      bar.style.cssText =
        'position:fixed; top:0; left:0; width:100vw; height:' + BAR_HEIGHT + 'px;' +
        'z-index:999999; overflow:hidden; background:#000; pointer-events:none;' +
        'border-bottom:1px solid rgba(0,255,136,0.35);' +
        'box-shadow:0 6px 34px rgba(0,255,136,0.25); font-family:Rajdhani,sans-serif;';
    } else {
      bar.style.cssText =
        'position:relative; width:100%; height:' + BAR_HEIGHT + 'px;' +
        'overflow:hidden; background:#000; font-family:Rajdhani,sans-serif;';
    }

    bar.innerHTML =
      '<style>' +
      "@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700;900&family=Rajdhani:wght@600;700&display=swap');" +
      '#' + BAR_ID + ' .turf{position:absolute;top:0;left:0;width:100%;height:' + TURF_HEIGHT + 'px;' +
        'background:repeating-linear-gradient(90deg,#14622a 0px,#14622a 42px,#1c8a3a 42px,#1c8a3a 84px);' +
        'animation:betbotTurfScroll 7s linear infinite;}' +
      '#' + BAR_ID + ' .turf:before{content:"";position:absolute;left:50%;top:0;bottom:0;width:2px;' +
        'background:rgba(255,255,255,.5);transform:translateX(-50%);box-shadow:0 0 8px rgba(255,255,255,.35);}' +
      '#' + BAR_ID + ' .turf:after{content:"";position:absolute;left:50%;top:50%;width:64px;height:64px;' +
        'border:2px solid rgba(255,255,255,.45);border-radius:50%;transform:translate(-50%,-50%);' +
        'box-shadow:0 0 10px rgba(255,255,255,.25);}' +
      '@keyframes betbotTurfScroll{from{background-position:0 0;}to{background-position:168px 0;}}' +
      '#' + BAR_ID + ' .shine{position:absolute;top:0;left:-40%;width:40%;height:' + TURF_HEIGHT + 'px;' +
        'background:linear-gradient(120deg,transparent,rgba(255,255,255,.18),transparent);' +
        'animation:betbotShine 4.5s linear infinite;}' +
      '@keyframes betbotShine{0%{left:-40%;}100%{left:120%;}}' +
      '#' + BAR_ID + ' canvas{position:absolute;top:0;left:0;width:100%;height:' + TURF_HEIGHT + 'px;}' +
      '#' + BAR_ID + ' .hero{position:absolute;top:' + TURF_HEIGHT + 'px;left:0;width:100%;' +
        'text-align:center;padding:10px 20px 12px;box-sizing:border-box;}' +
      '#' + BAR_ID + ' .title{font-family:Orbitron,monospace;font-size:2.3rem;font-weight:900;' +
        'letter-spacing:5px;margin:0;color:#00ff88;' +
        'text-shadow:0 0 8px #00ff88,0 0 25px #00cc66,0 0 55px #009944;' +
        'animation:betbotGlow 3s ease-in-out infinite;}' +
      '@keyframes betbotGlow{0%,100%{text-shadow:0 0 8px #00ff88,0 0 25px #00cc66,0 0 55px #009944;}' +
        '50%{text-shadow:0 0 18px #00ff88,0 0 45px #00cc66,0 0 90px #009944,0 0 120px #00ff88;}}' +
      '#' + BAR_ID + ' .subtitle{font-family:Rajdhani,sans-serif;color:#7fff7f;font-size:.85rem;' +
        'letter-spacing:4px;margin:6px 0 3px;text-transform:uppercase;}' +
      '#' + BAR_ID + ' .tagline{font-family:Rajdhani,sans-serif;color:rgba(0,255,136,.55);' +
        'font-size:.7rem;letter-spacing:2.5px;text-transform:uppercase;margin-bottom:10px;}' +
      '#' + BAR_ID + ' .badges{display:flex;justify-content:center;gap:8px;flex-wrap:wrap;pointer-events:auto;}' +
      '#' + BAR_ID + ' .badge{font-family:Orbitron,monospace;font-size:.55rem;font-weight:700;' +
        'letter-spacing:1.5px;padding:4px 12px;border-radius:20px;text-transform:uppercase;' +
        'border:1px solid;cursor:default;animation:betbotBadgePulse 4s ease-in-out infinite;' +
        'transition:transform .2s ease;}' +
      '#' + BAR_ID + ' .badge:hover{transform:translateY(-3px) scale(1.07);}' +
      '#' + BAR_ID + ' .b1{color:#00ff88;border-color:#00ff88;background:rgba(0,255,136,.08);' +
        'box-shadow:0 0 8px rgba(0,255,136,.25);}' +
      '#' + BAR_ID + ' .b2{color:#f5c518;border-color:#f5c518;background:rgba(245,197,24,.08);' +
        'box-shadow:0 0 8px rgba(245,197,24,.25);animation-delay:.8s;}' +
      '#' + BAR_ID + ' .b3{color:#00cfff;border-color:#00cfff;background:rgba(0,207,255,.08);' +
        'box-shadow:0 0 8px rgba(0,207,255,.25);animation-delay:1.6s;}' +
      '#' + BAR_ID + ' .b4{color:#ff6b6b;border-color:#ff6b6b;background:rgba(255,107,107,.08);' +
        'box-shadow:0 0 8px rgba(255,107,107,.2);animation-delay:2.4s;}' +
      '@keyframes betbotBadgePulse{0%,100%{opacity:.8;transform:scale(1);}50%{opacity:1;transform:scale(1.04);}}' +
      '</style>' +
      '<div class="turf"><div class="shine"></div></div>' +
      '<canvas></canvas>' +
      '<div class="hero">' +
      '  <div class="title">⚡ BETBOT AI</div>' +
      '  <div class="subtitle">Inteligência Artificial para Apostas Esportivas</div>' +
      '  <div class="tagline">Encontre value bets &middot; Simule retornos &middot; Maximize seu ROI</div>' +
      '  <div class="badges">' +
      '    <span class="badge b1">🟢 Value Betting</span>' +
      '    <span class="badge b2">🏆 Análise de Odds</span>' +
      '    <span class="badge b3">⚡ Simulação Instant</span>' +
      '    <span class="badge b4">🎯 Gestão de Banca</span>' +
      '  </div>' +
      '</div>';

    doc.body.appendChild(bar);

    var canvas = bar.querySelector('canvas');
    var ctx = canvas.getContext('2d');
    var winRef = isFixed ? window.parent : window;

    function resize() {
      canvas.width = winRef.innerWidth || 800;
      canvas.height = TURF_HEIGHT;
    }
    resize();
    if (winRef.__betbotResizeHandler) {
      winRef.removeEventListener('resize', winRef.__betbotResizeHandler);
    }
    winRef.__betbotResizeHandler = resize;
    winRef.addEventListener('resize', resize);

    var particles = [];
    function spawn() {
      var n = Math.floor(Math.random() * 4) + 1;
      for (var i = 0; i < n; i++) {
        particles.push({
          x: Math.random() * canvas.width,
          y: -4,
          r: Math.random() * 2.5 + 0.5,
          vx: (Math.random() - 0.5) * 0.6,
          vy: Math.random() * 1.7 + 0.5,
          opacity: 1,
          decay: Math.random() * 0.02 + 0.008,
          hue: Math.floor(Math.random() * 55 + 95),
        });
      }
    }
    function draw() {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      if (Math.random() < 0.55) spawn();
      for (var i = particles.length - 1; i >= 0; i--) {
        var p = particles[i];
        p.x += p.vx; p.y += p.vy; p.opacity -= p.decay;
        if (p.opacity <= 0 || p.y > canvas.height + 12) { particles.splice(i, 1); continue; }
        ctx.save();
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
        ctx.fillStyle = 'hsla(' + p.hue + ',100%,65%,' + p.opacity + ')';
        ctx.shadowBlur = 12;
        ctx.shadowColor = 'hsla(' + p.hue + ',100%,65%,' + p.opacity + ')';
        ctx.fill();
        ctx.restore();
      }
      winRef.__betbotAnim = winRef.requestAnimationFrame(draw);
    }
    draw();
  }

  try {
    var pDoc = window.parent.document;
    var old = pDoc.getElementById(BAR_ID);
    if (old) old.remove();
    var oldStyle = pDoc.getElementById(STYLE_ID);
    if (oldStyle) oldStyle.remove();
    if (window.parent.__betbotAnim) {
      window.parent.cancelAnimationFrame(window.parent.__betbotAnim);
    }

    var style = pDoc.createElement('style');
    style.id = STYLE_ID;
    style.innerHTML =
      '[data-testid="stAppViewContainer"] .block-container{padding-top:' + (BAR_HEIGHT + 24) + 'px !important;}' +
      'section[data-testid="stSidebar"] div[data-testid="stSidebarUserContent"]{padding-top:' + (BAR_HEIGHT + 16) + 'px !important;}' +
      '[data-testid="stHeader"]{background:transparent !important;}';
    pDoc.head.appendChild(style);

    renderInto(pDoc, true);

    if (window.frameElement) {
      window.frameElement.style.height = '0px';
      window.frameElement.style.minHeight = '0px';
    }
  } catch (e) {
    renderInto(document, false);
  }
})();
</script>
</body>
</html>
""", height=0)

# --- Session state ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                "Olá! 👋🎰 Sou o **BetBot**, seu assistente de apostas esportivas com IA. "
                "Pode me perguntar sobre odds, mercados, estratégias, bankroll e muito mais. "
                "Use também a aba **Simulação** para calcular seus retornos!"
            ),
        }
    ]
CHAT_HISTORY_FILE = Path(__file__).with_name("chat_history.json")
WELCOME_MESSAGE = {
    "role": "assistant",
    "content": (
        "Olá! 👋🎰 Sou o **BetBot**, seu assistente de apostas esportivas com IA. "
        "Pode me perguntar sobre odds, mercados, estratégias, bankroll e muito mais. "
        "Use também a aba **Simulação** para calcular seus retornos!"
    ),
}


def load_chat_history() -> list:
    try:
        with CHAT_HISTORY_FILE.open("r", encoding="utf-8") as file:
            chats = json.load(file)
        return chats if isinstance(chats, list) else []
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return []


def save_chat_history() -> None:
    try:
        with CHAT_HISTORY_FILE.open("w", encoding="utf-8") as file:
            json.dump(st.session_state.chats, file, ensure_ascii=False, indent=2)
    except OSError:
        st.sidebar.error("Não foi possível salvar o histórico dos chats.")


def create_chat() -> dict:
    timestamp = datetime.now().isoformat(timespec="seconds")
    return {
        "id": str(uuid4()),
        "title": "Novo chat",
        "created_at": timestamp,
        "updated_at": timestamp,
        "messages": [WELCOME_MESSAGE.copy()],
    }


def get_active_chat() -> dict:
    active_chat_id = st.session_state.active_chat_id
    for chat in st.session_state.chats:
        if chat.get("id") == active_chat_id:
            return chat

    chat = create_chat()
    st.session_state.chats.insert(0, chat)
    st.session_state.active_chat_id = chat["id"]
    save_chat_history()
    return chat


def select_chat(chat_id: str) -> None:
    st.session_state.active_chat_id = chat_id
    st.session_state.messages = get_active_chat()["messages"]


if "chats" not in st.session_state:
    st.session_state.chats = load_chat_history()
    if not st.session_state.chats:
        st.session_state.chats = [create_chat()]
        save_chat_history()

if "active_chat_id" not in st.session_state:
    st.session_state.active_chat_id = st.session_state.chats[0]["id"]

st.session_state.messages = get_active_chat()["messages"]

with st.sidebar:
    st.markdown("## ⚡ BetBot AI")
    if st.button("➕ Criar novo chat", use_container_width=True):
        chat = create_chat()
        st.session_state.chats.insert(0, chat)
        st.session_state.active_chat_id = chat["id"]
        st.session_state.messages = chat["messages"]
        save_chat_history()
        st.rerun()

    st.markdown("### 💬 Seus chats")
    for chat in st.session_state.chats:
        is_active = chat["id"] == st.session_state.active_chat_id
        label = f"{'▶ ' if is_active else ''}{chat.get('title', 'Novo chat')}"
        if st.button(label, key=f"chat_{chat['id']}", use_container_width=True):
            select_chat(chat["id"])
            st.rerun()

    st.divider()
    if st.button("🗑️ Limpar chat atual", use_container_width=True):
        active_chat = get_active_chat()
        active_chat["messages"] = [WELCOME_MESSAGE.copy()]
        active_chat["title"] = "Novo chat"
        active_chat["updated_at"] = datetime.now().isoformat(timespec="seconds")
        st.session_state.messages = active_chat["messages"]
        save_chat_history()
        st.rerun()

    st.markdown(
        "<div style='text-align:center; font-family:Orbitron,monospace; color:#00ff88; "
        "font-size:0.6rem; letter-spacing:2px; margin-top:1rem; "
        "text-shadow:0 0 8px rgba(0,255,136,0.5);'>"
        "BETBOT AI · POWERED BY AI</div>",
        unsafe_allow_html=True,
    )

if "sim_bets" not in st.session_state:
    st.session_state.sim_bets = []

if "multi_bets" not in st.session_state:
    st.session_state.multi_bets = []

BET_HISTORY_FILE = Path(__file__).with_name("bet_history.json")


def load_bet_history() -> list:
    try:
        with BET_HISTORY_FILE.open("r", encoding="utf-8") as file:
            bets = json.load(file)
        return bets if isinstance(bets, list) else []
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return []


def save_bet_history() -> None:
    try:
        with BET_HISTORY_FILE.open("w", encoding="utf-8") as file:
            json.dump(st.session_state.bet_history, file, ensure_ascii=False, indent=2)
    except OSError:
        st.error("Não foi possível salvar o histórico de bets.")


if "bet_history" not in st.session_state:
    st.session_state.bet_history = load_bet_history()

# --- Real AI engine (Anthropic Claude) ---
SYSTEM_PROMPT = """Você é o BetBot, um assistente de IA especializado EXCLUSIVAMENTE em apostas esportivas, com finalidade educacional.

Seu escopo cobre: odds, probabilidade implícita, handicap (asiático/europeu), over/under,
apostas múltiplas/acumuladores, value bets, gestão de banca (bankroll), cashout, ROI,
mercados de apostas (1X2, BTTS, dupla chance, placar exato, etc.), apostas ao vivo,
estratégias de apostas, bônus/promoções de casas de apostas, e apostas em geral (futebol e
outros esportes).

Regras:
- Responda sempre em português do Brasil, de forma clara, direta e didática, podendo usar
  emojis com moderação e markdown (negrito, listas) para organizar a explicação.
- O usuário pode fazer perguntas amplas, vagas ou genéricas — interprete a intenção e responda
  da forma mais útil possível dentro do seu escopo, mesmo sem palavras-chave exatas.
- Se a pergunta não tiver relação alguma com apostas esportivas (ex: receitas, programação,
  política, saúde etc.), NÃO responda ao conteúdo. Em vez disso, informe educadamente que
  esse não é o seu propósito e redirecione o usuário para temas de apostas esportivas.
- Sempre que fizer sentido, mencione que a aba "📊 Simulação" pode ser usada para calcular
  retornos de apostas simples ou múltiplas.
- Nunca incentive apostas irresponsáveis; quando relevante, reforce jogo responsável.
- Não forneça "dicas certeiras" de apostas nem garanta resultados de jogos futuros.
- Em perguntas educacionais sobre odds, probabilidades, mercados ou simulações, não introduza
    avisos ou barreiras jurídicas que não foram solicitados.
- Não afirme que apostas esportivas foram proibidas nem apresente supostas restrições legais
    como fatos. Se perguntarem diretamente sobre legislação, esclareça brevemente que o BetBot
    não presta consultoria jurídica e não invente informações sobre o tema.
"""
"""

def _get_client():
    api_key = st.secrets.get("ANTHROPIC_API_KEY", None) if hasattr(st, "secrets") else None
    if not api_key:
        return None
    return anthropic.Anthropic(api_key=api_key)

def get_bot_response(history: list) -> str:
    client = _get_client()
    if client is None:
        return (
            "⚠️ **Chave de API não configurada.**\n\n"
            "Para o BetBot responder de verdade, crie o arquivo `.streamlit/secrets.toml` "
            "na pasta do projeto com o conteúdo:\n\n"
            "```toml\nANTHROPIC_API_KEY = \"sua-chave-aqui\"\n```\n\n"
            "Obtenha sua chave em [console.anthropic.com](https://console.anthropic.com/settings/keys) "
            "e reinicie o app depois de salvar."
        )

    api_messages = [{"role": m["role"], "content": m["content"]} for m in history]
    # Anthropic requires the conversation to start with a "user" message;
    # drop the leading hardcoded greeting from the assistant if present.
    while api_messages and api_messages[0]["role"] != "user":
        api_messages.pop(0)

    try:
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=700,
            system=SYSTEM_PROMPT,
            messages=api_messages,
        )
        return response.content[0].text
    except anthropic.AuthenticationError:
        return "⚠️ Chave de API inválida. Verifique o valor de `ANTHROPIC_API_KEY` em `.streamlit/secrets.toml`."
    except anthropic.RateLimitError:
        return "⚠️ Limite de requisições atingido. Aguarde um instante e tente novamente."
    except Exception as e:
        return f"⚠️ Ocorreu um erro ao consultar a IA: `{e}`"

# ============================
# TABS
# ============================
tab_chat, tab_sim, tab_multi, tab_history = st.tabs(
    ["💬 Chat", "📊 Simulação", "🎯 Bet Múltipla", "📜 Histórico de Bets"]
)

# Bônus progressivo por nº de seleções (estilo "Acumulador Bônus" do bet365)
ACCA_BONUS_TABLE = [
    (8, 0.25),
    (7, 0.20),
    (6, 0.15),
    (5, 0.10),
    (4, 0.05),
]

def get_acca_bonus(n_selections: int) -> float:
    for min_legs, bonus in ACCA_BONUS_TABLE:
        if n_selections >= min_legs:
            return bonus
    return 0.0

# Bônus de correlação (estilo "Bet Builder" do bet365: combinar mercados do mesmo evento)
BET_BUILDER_BONUS_PER_EXTRA = 0.03
BET_BUILDER_BONUS_CAP = 0.15

def get_bet_builder_bonus(bets: list) -> float:
    events = {}
    for b in bets:
        events.setdefault(b["event"], []).append(b)
    total_bonus = 0.0
    for legs in events.values():
        if len(legs) >= 2:
            total_bonus += min((len(legs) - 1) * BET_BUILDER_BONUS_PER_EXTRA, BET_BUILDER_BONUS_CAP)
    return total_bonus

# ============================
# TAB CHAT
# ============================
with tab_chat:
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                st.markdown(
                    f'<div class="user-msg">'
                    f'<div class="msg-label user-label">👤 Você</div>'
                    f'{msg["content"]}'
                    f'</div>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f'<div class="bot-msg">'
                    f'<div class="msg-label bot-label">🎰 BetBot</div>'
                    f'{msg["content"]}'
                    f'</div>',
                    unsafe_allow_html=True,
                )

    st.divider()

    with st.form(key="chat_form", clear_on_submit=True):
        cols = st.columns([5, 1])
        user_input = cols[0].text_input(
            label="",
            placeholder="Pergunte sobre apostas... ex: O que é handicap?",
            label_visibility="collapsed",
        )
        submitted = cols[1].form_submit_button("Enviar 🎰")

    if submitted and user_input.strip():
        st.session_state.messages.append({"role": "user", "content": user_input.strip()})
        with st.spinner("BetBot está pensando... 🎰"):
            response = get_bot_response(st.session_state.messages)
        st.session_state.messages.append({"role": "assistant", "content": response})
        active_chat = get_active_chat()
        active_chat["updated_at"] = datetime.now().isoformat(timespec="seconds")
        if active_chat["title"] == "Novo chat":
            active_chat["title"] = user_input.strip()[:40]
        st.session_state.chats.sort(key=lambda chat: chat["updated_at"], reverse=True)
        save_chat_history()
        st.rerun()

# ============================
# TAB SIMULAÇÃO
# ============================
with tab_sim:
    st.markdown("### 📊 Simulador de Apostas")
    st.markdown(
        "Adicione suas apostas abaixo para simular o retorno esperado. "
        "Suporta apostas simples e múltiplas (acumulador)."
    )
    st.divider()

    # --- Formulário para adicionar aposta ---
    with st.form(key="sim_form", clear_on_submit=True):
        st.markdown("#### ➕ Adicionar seleção")
        c1, c2, c3, c4 = st.columns([3, 2, 2, 2])
        sel_name  = c1.text_input("Seleção", placeholder="Ex: Flamengo vence")
        sel_odd   = c2.number_input("Odd", min_value=1.01, max_value=1000.0, value=2.00, step=0.01, format="%.2f")
        sel_stake = c3.number_input("Valor (R$)", min_value=0.01, value=10.0, step=1.0, format="%.2f")
        sel_add   = c4.form_submit_button("Adicionar ➕")

    if sel_add and sel_name.strip():
        st.session_state.sim_bets.append({
            "name":  sel_name.strip(),
            "odd":   sel_odd,
            "stake": sel_stake,
        })
        st.rerun()

    # --- Lista de seleções ---
    if st.session_state.sim_bets:
        st.markdown("#### 🗂️ Seleções adicionadas")
        for i, bet in enumerate(st.session_state.sim_bets):
            col_a, col_b, col_c, col_d = st.columns([4, 2, 2, 1])
            col_a.markdown(f"**{bet['name']}**")
            col_b.markdown(f"Odd: `{bet['odd']:.2f}`")
            col_c.markdown(f"Stake: `R$ {bet['stake']:.2f}`")
            if col_d.button("✕", key=f"del_{i}"):
                st.session_state.sim_bets.pop(i)
                st.rerun()

        st.divider()

        # --- Resultados individuais ---
        st.markdown("#### 📈 Resumo por Aposta")
        for bet in st.session_state.sim_bets:
            implied_p = 1 / bet["odd"]
            pot_return = bet["stake"] * bet["odd"]
            pot_profit = pot_return - bet["stake"]
            ev_ind = (implied_p * pot_profit) - ((1 - implied_p) * bet["stake"])
            col1, col2, col3, col4 = st.columns(4)
            col1.metric(bet["name"], f"Odd {bet['odd']:.2f}")
            col2.metric("Stake", f"R$ {bet['stake']:.2f}")
            col3.metric("Retorno Potencial", f"R$ {pot_return:.2f}")
            col4.metric("EV", f"R$ {ev_ind:.2f}")

        st.divider()

        # --- Distribuição de cenários ---
        st.markdown("#### 🎲 Distribuição de Cenários")
        st.markdown(
            "Clique no botão abaixo para ver **todos os cenários possíveis**, "
            "suas probabilidades e o retorno líquido de cada um."
        )

        if st.button("🔍 Calcular todos os cenários"):
            import itertools

            n = len(st.session_state.sim_bets)
            outcomes = list(itertools.product([True, False], repeat=n))

            scenario_data = []
            for outcome in outcomes:
                # Label do cenário
                labels = []
                for j, won in enumerate(outcome):
                    bet = st.session_state.sim_bets[j]
                    short = bet["name"][:18] + ("…" if len(bet["name"]) > 18 else "")
                    labels.append(f"✅ {short}" if won else f"❌ {short}")
                scenario_label = " | ".join(labels)

                # Probabilidade do cenário (produto das probs individuais)
                prob = 1.0
                for j, won in enumerate(outcome):
                    p = 1 / st.session_state.sim_bets[j]["odd"]
                    prob *= p if won else (1 - p)

                # Retorno líquido: soma dos lucros/perdas de cada aposta
                net = 0.0
                for j, won in enumerate(outcome):
                    bet = st.session_state.sim_bets[j]
                    if won:
                        net += bet["stake"] * (bet["odd"] - 1)   # lucro
                    else:
                        net -= bet["stake"]                        # perda

                scenario_data.append({
                    "scenario": scenario_label,
                    "prob":     prob,
                    "net":      net,
                })

            # Ordenar por probabilidade decrescente
            scenario_data.sort(key=lambda x: x["prob"], reverse=True)

            # EV total
            ev_total = sum(s["prob"] * s["net"] for s in scenario_data)
            total_staked = sum(b["stake"] for b in st.session_state.sim_bets)

            ev_color_span = '<span style="color:#ff6b6b">negativo ⚠️</span>' if ev_total < 0 else '<span style="color:#00ff88">positivo ✅</span>'

            st.markdown(
                f"<div class='bot-msg'>"
                f"<div class='msg-label bot-label'>🎰 BetBot — Valor Esperado Total</div>"
                f"Total apostado: <b>R$ {total_staked:.2f}</b> · "
                f"EV esperado no longo prazo: <b>R$ {ev_total:.2f}</b> "
                f"({ev_color_span})"
                f"</div>",
                unsafe_allow_html=True
            )

            st.markdown("")
            for s in scenario_data:
                net_color  = "#00ff88" if s["net"] >= 0 else "#ff6b6b"
                net_sign   = "+" if s["net"] >= 0 else ""
                bar_width  = max(4, int(s["prob"] * 100 * 2))   # escala visual
                st.markdown(
                    f"<div style='background:rgba(0,255,136,0.04);border-left:3px solid rgba(0,255,136,0.25);"
                    f"border-radius:0 8px 8px 0;padding:10px 14px;margin:6px 0;'>"
                    f"<div style='font-family:Rajdhani,sans-serif;font-size:0.9rem;color:#d0f0d0;margin-bottom:6px;'>"
                    f"{s['scenario']}</div>"
                    f"<div style='display:flex;align-items:center;gap:14px;flex-wrap:wrap;'>"
                    f"<span style='font-family:Orbitron,monospace;font-size:0.7rem;color:#7fff7f;"
                    f"letter-spacing:1px;'>PROB <b style='color:#00ff88'>{s['prob']*100:.2f}%</b></span>"
                    f"<div style='flex:1;min-width:80px;background:rgba(255,255,255,0.06);"
                    f"border-radius:4px;height:8px;'>"
                    f"<div style='width:{bar_width}%;background:linear-gradient(90deg,#00ff88,#00cfff);"
                    f"height:8px;border-radius:4px;'></div></div>"
                    f"<span style='font-family:Orbitron,monospace;font-size:0.7rem;"
                    f"color:{net_color};letter-spacing:1px;'>LÍQUIDO <b>{net_sign}R$ {s['net']:.2f}</b></span>"
                    f"</div></div>",
                    unsafe_allow_html=True
                )

        st.divider()
        if st.button("🗑️ Limpar simulação"):
            st.session_state.sim_bets = []
            st.rerun()
    else:
        st.info("Nenhuma seleção adicionada ainda. Use o formulário acima para começar! 🎰")

# ============================
# TAB BET MÚLTIPLA
# ============================
with tab_multi:
    st.markdown("### 🎯 Bet Múltipla — estilo bet365")
    st.markdown(
        "Monte sua aposta múltipla (acumulador) combinando seleções de um ou mais eventos. "
        "A odd final pode ser **impulsionada automaticamente** dependendo da composição escolhida:\n\n"
        "- 🚀 **Bônus de Acumulador**: quanto mais seleções na múltipla, maior o bônus sobre a odd combinada "
        "(a partir de 4 seleções).\n"
        "- 🧩 **Bônus Bet Builder**: combinar 2 ou mais mercados do **mesmo evento** (ex: resultado final + "
        "ambas marcam do mesmo jogo) gera um bônus extra por correlação."
    )
    st.divider()

    with st.form(key="multi_form", clear_on_submit=True):
        st.markdown("#### ➕ Adicionar seleção à múltipla")
        m1, m2, m3, m4 = st.columns([3, 2, 3, 2])
        multi_event  = m1.text_input("Evento", placeholder="Ex: Flamengo x Palmeiras")
        multi_market = m2.selectbox(
            "Mercado",
            ["Resultado Final", "Ambas Marcam", "Total de Gols", "Handicap Asiático", "Cartões", "Escanteios", "Outro"],
        )
        multi_name = m3.text_input("Seleção", placeholder="Ex: Flamengo vence")
        multi_odd  = m4.number_input("Odd", min_value=1.01, max_value=1000.0, value=1.80, step=0.01, format="%.2f")
        multi_add  = st.form_submit_button("Adicionar ➕")

    if multi_add and multi_event.strip() and multi_name.strip():
        st.session_state.multi_bets.append({
            "event":  multi_event.strip(),
            "market": multi_market,
            "name":   multi_name.strip(),
            "odd":    multi_odd,
        })
        st.rerun()

    if st.session_state.multi_bets:
        st.markdown("#### 🗂️ Seleções da múltipla")
        for i, leg in enumerate(st.session_state.multi_bets):
            col_a, col_b, col_c, col_d = st.columns([3, 3, 2, 1])
            col_a.markdown(f"**{leg['event']}**")
            col_b.markdown(f"{leg['market']}: `{leg['name']}`")
            col_c.markdown(f"Odd: `{leg['odd']:.2f}`")
            if col_d.button("✕", key=f"del_multi_{i}"):
                st.session_state.multi_bets.pop(i)
                st.rerun()

        st.divider()
        multi_stake = st.number_input(
            "Valor da aposta (R$)", min_value=0.01, value=10.0, step=1.0, format="%.2f", key="multi_stake"
        )

        n_legs = len(st.session_state.multi_bets)
        base_odd = 1.0
        for leg in st.session_state.multi_bets:
            base_odd *= leg["odd"]

        acca_bonus = get_acca_bonus(n_legs) if n_legs >= 2 else 0.0
        builder_bonus = get_bet_builder_bonus(st.session_state.multi_bets)
        total_bonus = acca_bonus + builder_bonus
        boosted_odd = base_odd * (1 + total_bonus)

        base_return = multi_stake * base_odd
        boosted_return = multi_stake * boosted_odd

        st.markdown("#### 🚀 Odd impulsionada")
        b1, b2, b3, b4 = st.columns(4)
        b1.metric("Odd combinada", f"{base_odd:.2f}")
        b2.metric("Bônus acumulador", f"+{acca_bonus*100:.0f}%")
        b3.metric("Bônus bet builder", f"+{builder_bonus*100:.0f}%")
        b4.metric("Odd final", f"{boosted_odd:.2f}")

        st.markdown(
            f"<div class='bot-msg'>"
            f"<div class='msg-label bot-label'>🎰 BetBot — Resumo da Múltipla</div>"
            f"Seleções: <b>{n_legs}</b> · Stake: <b>R$ {multi_stake:.2f}</b><br>"
            f"Retorno sem boost: <b>R$ {base_return:.2f}</b> · "
            f"Retorno com boost: <b style='color:#00ff88'>R$ {boosted_return:.2f}</b> "
            f"(+R$ {boosted_return - base_return:.2f})"
            f"</div>",
            unsafe_allow_html=True
        )

        if n_legs < 2:
            st.info("Adicione pelo menos 2 seleções para formar uma múltipla e habilitar os bônus.")

        st.divider()

        # --- Probabilidade e distribuição de cenários ---
        st.markdown("#### 🎲 Probabilidade e Distribuição de Cenários")
        combined_prob = 1.0
        for leg in st.session_state.multi_bets:
            combined_prob *= (1 / leg["odd"])
        st.metric("Probabilidade de a múltipla ocorrer (todos os eventos baterem)", f"{combined_prob*100:.2f}%")

        st.markdown(
            "Clique no botão abaixo para ver a **distribuição de todos os cenários possíveis** "
            "(combinações de acerto/erro de cada evento) em barras verticais."
        )

        if st.button("🔍 Calcular distribuição de cenários", key="multi_scenarios_btn"):
            import itertools

            outcomes = list(itertools.product([True, False], repeat=n_legs))
            scenario_data = []
            for outcome in outcomes:
                labels = []
                prob = 1.0
                for j, won in enumerate(outcome):
                    leg = st.session_state.multi_bets[j]
                    p = 1 / leg["odd"]
                    prob *= p if won else (1 - p)
                    short = leg["name"][:16] + ("…" if len(leg["name"]) > 16 else "")
                    labels.append(f"✅ {short}" if won else f"❌ {short}")
                all_won = all(outcome)
                net = (boosted_return - multi_stake) if all_won else -multi_stake
                scenario_data.append({
                    "label": " | ".join(labels),
                    "prob":  prob,
                    "net":   net,
                    "won":   all_won,
                })

            scenario_data.sort(key=lambda x: x["prob"], reverse=True)

            max_display = 16
            display_data = scenario_data[:max_display]
            if len(scenario_data) > max_display:
                st.caption(
                    f"Mostrando os {max_display} cenários mais prováveis de {len(scenario_data)} combinações totais."
                )

            max_prob = max(s["prob"] for s in display_data) if display_data else 1.0

            # Barras verticais: altura proporcional à probabilidade do cenário
            bars_html = (
                "<div style='display:flex;align-items:flex-end;gap:10px;height:220px;"
                "overflow-x:auto;padding:16px 6px 8px;border-bottom:1px solid rgba(0,255,136,0.15);'>"
            )
            for idx, s in enumerate(display_data, start=1):
                bar_h = max(4, int((s["prob"] / max_prob) * 170))
                color = "#00ff88" if s["won"] else "#ff6b6b"
                bars_html += (
                    f"<div style='display:flex;flex-direction:column;align-items:center;min-width:46px;' title='{s['label']}'>"
                    f"<div style='font-family:Orbitron,monospace;font-size:0.6rem;color:{color};margin-bottom:4px;white-space:nowrap;'>"
                    f"{s['prob']*100:.1f}%</div>"
                    f"<div style='width:26px;height:{bar_h}px;background:linear-gradient(180deg,{color},rgba(0,0,0,0.05));"
                    f"border-radius:4px 4px 0 0;box-shadow:0 0 8px {color}55;'></div>"
                    f"<div style='font-family:Orbitron,monospace;font-size:0.6rem;color:#7fff7f;margin-top:6px;'>#{idx}</div>"
                    f"</div>"
                )
            bars_html += "</div>"
            st.markdown(bars_html, unsafe_allow_html=True)

            st.markdown("")
            for idx, s in enumerate(display_data, start=1):
                net_color = "#00ff88" if s["won"] else "#ff6b6b"
                net_sign = "+" if s["net"] >= 0 else ""
                st.markdown(
                    f"<div style='font-family:Rajdhani,sans-serif;font-size:0.85rem;color:#d0f0d0;margin:2px 0;'>"
                    f"<b style='color:#7fff7f'>#{idx}</b> {s['label']} — "
                    f"<span style='color:#7fff7f'>{s['prob']*100:.2f}%</span> — "
                    f"<span style='color:{net_color}'>{net_sign}R$ {s['net']:.2f}</span>"
                    f"</div>",
                    unsafe_allow_html=True
                )

        st.divider()
        if st.button("🗑️ Limpar múltipla"):
            st.session_state.multi_bets = []
            st.rerun()
    else:
        st.info("Nenhuma seleção adicionada ainda. Use o formulário acima para montar sua múltipla! 🎯")

# ============================
# TAB HISTÓRICO DE BETS
# ============================
with tab_history:
    st.markdown("### 📜 Histórico de Bets")
    st.markdown(
        "Registre apostas já encerradas. Informe o retorno **bruto** recebido; em caso de perda, use `R$ 0,00`."
    )

    with st.form(key="bet_history_form", clear_on_submit=True):
        st.markdown("#### ➕ Registrar resultado")
        h1, h2, h3, h4 = st.columns([3, 2, 2, 2])
        history_name = h1.text_input("Aposta", placeholder="Ex: Flamengo vence")
        history_date = h2.date_input("Data", value=date.today(), format="DD/MM/YYYY")
        history_stake = h3.number_input(
            "Valor apostado (R$)", min_value=0.01, value=10.0, step=1.0, format="%.2f"
        )
        history_return = h4.number_input(
            "Retorno bruto (R$)", min_value=0.0, value=0.0, step=1.0, format="%.2f"
        )
        add_history = st.form_submit_button("Salvar resultado")

    if add_history and history_name.strip():
        st.session_state.bet_history.append({
            "name": history_name.strip(),
            "date": history_date.isoformat(),
            "stake": history_stake,
            "gross_return": history_return,
        })
        st.session_state.bet_history.sort(key=lambda bet: bet["date"], reverse=True)
        save_bet_history()
        st.rerun()

    if st.session_state.bet_history:
        total_staked = sum(bet["stake"] for bet in st.session_state.bet_history)
        total_return = sum(bet["gross_return"] for bet in st.session_state.bet_history)
        net_result = total_return - total_staked
        roi = net_result / total_staked if total_staked else 0.0

        bet_dates = [date.fromisoformat(bet["date"]) for bet in st.session_state.bet_history]
        tracking_days = max((max(bet_dates) - min(bet_dates)).days + 1, 1)
        projected_annual_stake = total_staked / tracking_days * 365
        projected_annual_bet_result = projected_annual_stake * roi

        st.divider()
        st.markdown("#### 📈 Desempenho das bets")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total apostado", f"R$ {total_staked:.2f}")
        m2.metric("Resultado líquido", f"R$ {net_result:.2f}")
        m3.metric("ROI realizado", f"{roi * 100:.2f}%")
        m4.metric("Projeção anual", f"R$ {projected_annual_bet_result:.2f}")
        st.caption(
            f"Projeção baseada no ROI do histórico e no ritmo de apostas dos últimos {tracking_days} dia(s). "
            "Não representa garantia de resultado."
        )

        st.markdown("#### 🏦 Comparação com CDI")
        cdi_rate = st.number_input(
            "CDI anual estimado (%)", min_value=0.0, max_value=100.0, value=14.15, step=0.01, format="%.2f"
        ) / 100
        cdi_annual_profit = total_staked * cdi_rate
        cdi_annual_total = total_staked + cdi_annual_profit
        c1, c2, c3 = st.columns(3)
        c1.metric("Capital aplicado no CDI", f"R$ {total_staked:.2f}")
        c2.metric("Rendimento em 1 ano", f"R$ {cdi_annual_profit:.2f}")
        c3.metric("Total após 1 ano", f"R$ {cdi_annual_total:.2f}")
        st.caption(
            "O CDI usa somente o dinheiro apostado em cada registro. Retornos e lucros das bets não entram no capital simulado."
        )

        st.markdown("#### 🗂️ Lançamentos")
        for index, bet in enumerate(st.session_state.bet_history):
            net = bet["gross_return"] - bet["stake"]
            net_color = "#00ff88" if net >= 0 else "#ff6b6b"
            col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 2, 1])
            col1.markdown(f"**{bet['name']}**")
            col2.markdown(date.fromisoformat(bet["date"]).strftime("%d/%m/%Y"))
            col3.markdown(f"Apostado: `R$ {bet['stake']:.2f}`")
            col4.markdown(
                f"<span style='color:{net_color}'>Líquido: R$ {net:.2f}</span>",
                unsafe_allow_html=True,
            )
            if col5.button("✕", key=f"delete_history_{index}"):
                st.session_state.bet_history.pop(index)
                save_bet_history()
                st.rerun()

        if st.button("🗑️ Limpar histórico de bets"):
            st.session_state.bet_history = []
            save_bet_history()
            st.rerun()
    else:
        st.info("Nenhuma bet registrada. Adicione um resultado encerrado para acompanhar seu desempenho.")