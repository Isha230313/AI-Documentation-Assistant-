import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from embedding import get_embeddings
from vector import get_retriever
from rag import build_chain, ask

st.set_page_config(
    page_title="AI Documentation Assistant",
    page_icon="📚",
    layout="centered",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

* { box-sizing: border-box; }
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stSidebar"] { display: none; }
[data-testid="stHeader"] { display: none; }
[data-testid="stSidebarNav"] { display: none; }
[data-testid="stNavLink"] { display: none; }
.block-container { padding-top: 0 !important; max-width: 760px !important; }

/* ══════════════════════════════════
   BACKGROUND + ANIMATED ORBS
══════════════════════════════════ */
.stApp {
    background: #07030f;
    min-height: 100vh;
    overflow-x: hidden;
}
.stApp::before {
    content: '';
    position: fixed;
    top: -180px; left: -180px;
    width: 550px; height: 550px;
    background: radial-gradient(circle, rgba(99,102,241,0.3) 0%, transparent 65%);
    border-radius: 50%;
    animation: orb1 14s ease-in-out infinite alternate;
    pointer-events: none; z-index: 0;
}
.stApp::after {
    content: '';
    position: fixed;
    bottom: -160px; right: -160px;
    width: 520px; height: 520px;
    background: radial-gradient(circle, rgba(236,72,153,0.28) 0%, transparent 65%);
    border-radius: 50%;
    animation: orb2 11s ease-in-out infinite alternate;
    pointer-events: none; z-index: 0;
}
@keyframes orb1 {
    from { transform: translate(0,0) scale(1); }
    to   { transform: translate(70px, 50px) scale(1.2); }
}
@keyframes orb2 {
    from { transform: translate(0,0) scale(1); }
    to   { transform: translate(-50px, -70px) scale(1.15); }
}


/* ══════════════════════════════════
   HERO
══════════════════════════════════ */
.hero {
    text-align: center;
    padding: 60px 24px 44px;
    position: relative; z-index: 1;
}
.hero-eyebrow {
    display: inline-flex; align-items: center; gap: 6px;
    background: rgba(99,102,241,0.15);
    border: 1px solid rgba(99,102,241,0.35);
    border-radius: 99px;
    padding: 6px 18px;
    font-size: 12px; font-weight: 600;
    color: #a5b4fc; letter-spacing: 0.8px;
    margin-bottom: 22px;
}
.hero-title {
    font-size: 3.2rem; font-weight: 900;
    line-height: 1.1; letter-spacing: -1.5px;
    color: white; margin-bottom: 16px;
}
.hero-title span {
    background: linear-gradient(135deg, #818cf8, #c084fc, #f472b6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.hero-sub {
    font-size: 1rem; color: rgba(255,255,255,0.4);
    font-weight: 400; line-height: 1.7;
    max-width: 400px; margin: 0 auto;
}

/* ══════════════════════════════════
   EMPTY STATE
══════════════════════════════════ */
.empty-wrap {
    display: flex; flex-direction: column; align-items: center;
    gap: 16px; padding: 20px 0 40px;
    position: relative; z-index: 1;
}
.suggestion-label {
    font-size: 12px; font-weight: 600;
    color: rgba(255,255,255,0.3);
    letter-spacing: 1px; text-transform: uppercase;
    margin-bottom: 4px;
}
.suggestions {
    display: flex; flex-wrap: wrap; gap: 10px; justify-content: center;
}
.suggestion-chip {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 12px; padding: 10px 18px;
    font-size: 13px; color: rgba(255,255,255,0.6);
    font-weight: 500; cursor: pointer;
    backdrop-filter: blur(8px);
    transition: all 0.2s;
}
.suggestion-chip:hover {
    background: rgba(99,102,241,0.15);
    border-color: rgba(99,102,241,0.4);
    color: #a5b4fc;
}

/* ══════════════════════════════════
   CHAT MESSAGES
══════════════════════════════════ */
.stChatMessage {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.09) !important;
    border-radius: 20px !important;
    margin-bottom: 12px !important;
    backdrop-filter: blur(12px) !important;
    position: relative; z-index: 1;
}
.stChatMessage p,
.stChatMessage li,
.stChatMessage code { color: #e2e8f0 !important; }
.stChatMessage code {
    background: rgba(255,255,255,0.08) !important;
    border-radius: 6px !important;
    padding: 2px 6px !important;
    font-size: 13px !important;
}

/* User bubble accent */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
    border-color: rgba(99,102,241,0.25) !important;
    background: rgba(99,102,241,0.07) !important;
}

/* ══════════════════════════════════
   CHAT INPUT
══════════════════════════════════ */
[data-testid="stChatInput"] {
    background: rgba(255,255,255,0.06) !important;
    border: 2px solid rgba(255,255,255,0.12) !important;
    border-radius: 18px !important;
    backdrop-filter: blur(16px) !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
    position: relative; z-index: 1;
}
[data-testid="stChatInput"]:focus-within {
    border-color: rgba(99,102,241,0.6) !important;
    box-shadow: 0 0 0 4px rgba(99,102,241,0.12) !important;
}
[data-testid="stChatInput"] textarea {
    color: #e2e8f0 !important;
    font-size: 15px !important;
    font-weight: 400 !important;
}
[data-testid="stChatInput"] textarea::placeholder {
    color: rgba(255,255,255,0.25) !important;
}

/* ══════════════════════════════════
   EXPANDER (Sources)
══════════════════════════════════ */
.streamlit-expanderHeader {
    background: rgba(255,255,255,0.04) !important;
    border-radius: 10px !important;
    color: #a5b4fc !important;
    font-size: 12px !important; font-weight: 600 !important;
}
.streamlit-expanderContent {
    color: #94a3b8 !important; font-size: 13px !important;
}

/* ══════════════════════════════════
   CLEAR BUTTON
══════════════════════════════════ */
.stButton > button {
    background: rgba(255,255,255,0.06) !important;
    color: rgba(255,255,255,0.45) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 10px !important;
    font-size: 12px !important; font-weight: 600 !important;
    padding: 6px 16px !important;
    transition: all 0.2s ease !important;
    letter-spacing: 0.3px !important;
    position: relative; z-index: 1;
}
.stButton > button:hover {
    background: rgba(239,68,68,0.12) !important;
    border-color: rgba(239,68,68,0.3) !important;
    color: #fca5a5 !important;
}
</style>
""", unsafe_allow_html=True)

# ── Hero ──────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-eyebrow">✦ &nbsp; AI-Powered Knowledge Base</div>
    <div class="hero-title">
        Ask anything.<br><span>Get instant answers.</span>
    </div>
    <div class="hero-sub">
        Every answer is pulled directly from your documentation — no guessing, no hallucinations.
    </div>
</div>
""", unsafe_allow_html=True)

# ── RAG setup ─────────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def load_rag():
    embeddings = get_embeddings()
    retriever  = get_retriever(embeddings)
    chain      = build_chain(retriever)
    return retriever, chain

# ── Session state ─────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

# ── Empty state ───────────────────────────────────────────────
if not st.session_state.messages:
    st.markdown("""
    <div class="empty-wrap">
        <div class="suggestion-label">Try asking</div>
        <div class="suggestions">
            <div class="suggestion-chip">📖 How do I get started?</div>
            <div class="suggestion-chip">🔧 How does it work?</div>
            <div class="suggestion-chip">❓ What are the key features?</div>
            <div class="suggestion-chip">🚀 Show me an example</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ── Clear button ──────────────────────────────────────────────
if st.session_state.messages:
    if st.button("🗑️  Clear chat"):
        st.session_state.messages = []
        st.rerun()

# ── Chat history ──────────────────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("sources"):
            with st.expander("📎 Sources"):
                for src in msg["sources"]:
                    st.markdown(f"- `{src}`")

# ── Input ─────────────────────────────────────────────────────
question = st.chat_input("Ask a question about your docs…")

if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Searching docs…"):
            retriever, chain = load_rag()
            response = ask(question, chain, retriever)
        st.markdown(response["answer"])
        if response["sources"]:
            with st.expander("📎 Sources"):
                for src in response["sources"]:
                    st.markdown(f"- `{src}`")

    st.session_state.messages.append({
        "role":    "assistant",
        "content": response["answer"],
        "sources": response["sources"],
    })
