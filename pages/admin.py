import sys
import os
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "src"))

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from ingest import load_document, load_all
from chunking import split_documents
from embedding import get_embeddings
from vector import store_chunks, get_client
from config import SUPPORTED_EXTENSIONS

st.set_page_config(
    page_title="Admin — Documentation Assistant",
    page_icon="🛠️",
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

/* ── Background ── */
.stApp {
    background: #f0f4ff;
    min-height: 100vh;
}

/* ── Navbar ── */
.navbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 16px 32px;
    background: white;
    border-bottom: 1px solid #e8ecf4;
    margin-bottom: 0;
}
.navbar-brand {
    font-size: 16px;
    font-weight: 800;
    color: #1a1a2e;
    display: flex;
    align-items: center;
    gap: 8px;
}
.navbar-badge {
    font-size: 12px;
    font-weight: 700;
    padding: 5px 14px;
    border-radius: 20px;
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    color: white;
    letter-spacing: 0.5px;
}

/* ── Hero banner ── */
.hero-banner {
    background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #ec4899 100%);
    padding: 48px 40px;
    text-align: center;
    margin-bottom: 36px;
    position: relative;
    overflow: hidden;
}
.hero-banner::before {
    content: '';
    position: absolute;
    top: -60px; left: -60px;
    width: 200px; height: 200px;
    background: rgba(255,255,255,0.08);
    border-radius: 50%;
}
.hero-banner::after {
    content: '';
    position: absolute;
    bottom: -80px; right: -40px;
    width: 250px; height: 250px;
    background: rgba(255,255,255,0.06);
    border-radius: 50%;
}
.hero-title {
    font-size: 2.2rem;
    font-weight: 900;
    color: white;
    margin-bottom: 8px;
    letter-spacing: -0.5px;
    position: relative;
    z-index: 1;
}
.hero-sub {
    color: rgba(255,255,255,0.8);
    font-size: 1rem;
    font-weight: 400;
    position: relative;
    z-index: 1;
}

/* ── Stat pills at top ── */
.stat-bar {
    display: flex;
    gap: 16px;
    justify-content: center;
    margin-top: 24px;
    position: relative;
    z-index: 1;
}
.stat-pill {
    background: rgba(255,255,255,0.18);
    backdrop-filter: blur(8px);
    border: 1px solid rgba(255,255,255,0.3);
    border-radius: 99px;
    padding: 8px 20px;
    color: white;
    font-size: 13px;
    font-weight: 600;
    display: flex;
    align-items: center;
    gap: 6px;
}
.stat-pill span { font-size: 16px; font-weight: 900; }

/* ── Section cards ── */
.upload-card {
    background: white;
    border-radius: 24px;
    padding: 32px;
    margin-bottom: 20px;
    border: 2px solid transparent;
    box-shadow: 0 4px 24px rgba(99,102,241,0.08);
    transition: box-shadow 0.3s;
}
.upload-card:hover {
    box-shadow: 0 8px 40px rgba(99,102,241,0.15);
}

.card-header {
    display: flex;
    align-items: center;
    gap: 16px;
    margin-bottom: 24px;
}
.card-emoji {
    width: 52px;
    height: 52px;
    border-radius: 16px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 24px;
    flex-shrink: 0;
}
.emoji-purple { background: linear-gradient(135deg, #ede9fe, #ddd6fe); }
.emoji-blue   { background: linear-gradient(135deg, #dbeafe, #bfdbfe); }
.card-header-text h3 {
    font-size: 17px;
    font-weight: 800;
    color: #1a1a2e;
    margin: 0 0 3px;
}
.card-header-text p {
    font-size: 13px;
    color: #6b7280;
    margin: 0;
}

/* ── File uploader override ── */
[data-testid="stFileUploader"] > div {
    background: #fafbff !important;
    border: 2px dashed #c7d2fe !important;
    border-radius: 16px !important;
    padding: 8px !important;
    transition: all 0.2s !important;
}
[data-testid="stFileUploader"] > div:hover {
    border-color: #6366f1 !important;
    background: #f0f4ff !important;
}
[data-testid="stFileUploader"] * { color: #4b5563 !important; }

/* ── Text area ── */
.stTextArea textarea {
    background: #fafbff !important;
    border: 2px solid #e8ecf4 !important;
    border-radius: 14px !important;
    color: #1a1a2e !important;
    font-size: 14px !important;
    line-height: 1.7 !important;
    padding: 14px !important;
    transition: border-color 0.2s !important;
}
.stTextArea textarea:focus {
    border-color: #6366f1 !important;
    box-shadow: 0 0 0 4px rgba(99,102,241,0.1) !important;
}
.stTextArea textarea::placeholder { color: #9ca3af !important; }

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
    color: white !important;
    border: none !important;
    border-radius: 14px !important;
    font-weight: 700 !important;
    font-size: 15px !important;
    padding: 14px 28px !important;
    transition: all 0.25s ease !important;
    box-shadow: 0 4px 18px rgba(99,102,241,0.35) !important;
    letter-spacing: 0.2px !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 28px rgba(99,102,241,0.5) !important;
}
.stButton > button:active { transform: translateY(0px) !important; }

/* ── Progress bar ── */
.stProgress > div > div {
    background: linear-gradient(90deg, #6366f1, #ec4899) !important;
    border-radius: 99px !important;
}
[data-testid="stProgressBar"] {
            
    background: #e8ecf4 !important;
    border-radius: 99px !important;
}

/* ── Alerts ── */
.stAlert {
    border-radius: 14px !important;
    font-size: 14px !important;
    font-weight: 500 !important;
}

/* ── Labels ── */
label { color: #374151 !important; font-size: 13px !important; font-weight: 500 !important; }

/* ── Divider ── */
hr { border-color: #e8ecf4 !important; margin: 8px 0 24px !important; }
</style>
""", unsafe_allow_html=True)

# ── Navbar ────────────────────────────────────────────────────
st.markdown("""
<div class="navbar">
    <div class="navbar-brand">📚 Documentation Assistant</div>
    <div class="navbar-badge">⚙️ Admin</div>
</div>
""", unsafe_allow_html=True)

# ── Fetch stats for hero ──────────────────────────────────────
total_vectors = 0
total_collections = 0
try:
    client = get_client()
    collections = client.get_collections().collections
    total_collections = len(collections)
    for col in collections:
        total_vectors += client.get_collection(col.name).points_count
    client.close()
except:
    pass

# ── Hero Banner ───────────────────────────────────────────────
st.markdown(f"""
<div class="hero-banner">
    <div class="hero-title">📂 Document Management</div>
    <div class="hero-sub">Upload files or add URLs — users can instantly search and ask questions from them.</div>
    <div class="stat-bar">
        <div class="stat-pill">🗄️ Collections &nbsp;<span>{total_collections}</span></div>
        <div class="stat-pill">🔢 Vectors &nbsp;<span>{total_vectors:,}</span></div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Upload Files Card ─────────────────────────────────────────
st.markdown("""
<div class="upload-card">
    <div class="card-header">
        <div class="card-emoji emoji-purple">📄</div>
        <div class="card-header-text">
            <h3>Upload Documents</h3>
            <p>Supports PDF, DOCX and TXT files · Max 50 MB per file</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

uploaded_files = st.file_uploader(
    label="upload",
    label_visibility="collapsed",
    type=["pdf", "docx", "txt"],
    accept_multiple_files=True,
)

if st.button("⚡  Ingest Files", use_container_width=True, key="btn_files"):
    if not uploaded_files:
        st.warning("Please upload at least one file first.")
    else:
        all_chunks = []
        bar = st.progress(0, text="Preparing…")
        for i, f in enumerate(uploaded_files):
            suffix = os.path.splitext(f.name)[1]
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp.write(f.read())
                tmp_path = tmp.name
            try:
                bar.progress((i + 1) / len(uploaded_files), text=f"Processing {f.name}…")
                docs = load_document(tmp_path)
                for doc in docs:
                    doc.metadata["source"] = f.name
                chunks = split_documents(docs)
                all_chunks.extend(chunks)
            except Exception as e:
                st.error(f"**{f.name}** — {e}")
            finally:
                os.unlink(tmp_path)
        if all_chunks:
            bar.progress(1.0, text="Storing in vector database…")
            store_chunks(all_chunks, get_embeddings())
            bar.empty()
            st.success(f"✅  {len(uploaded_files)} file(s) ingested successfully — {len(all_chunks):,} chunks added.")

st.markdown("<br>", unsafe_allow_html=True)

# ── URL Card ──────────────────────────────────────────────────
st.markdown("""
<div class="upload-card">
    <div class="card-header">
        <div class="card-emoji emoji-blue">🔗</div>
        <div class="card-header-text">
            <h3>Ingest from URLs</h3>
            <p>Paste web page links — we'll scrape and index the content automatically</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

url_input = st.text_area(
    label="urls",
    label_visibility="collapsed",
    height=130,
    placeholder="https://docs.yoursite.com/getting-started\nhttps://docs.yoursite.com/api-reference\nhttps://...",
)

if st.button("🌐  Ingest URLs", use_container_width=True, key="btn_urls"):
    urls = [u.strip() for u in url_input.splitlines() if u.strip()]
    if not urls:
        st.warning("Please enter at least one URL.")
    else:
        with st.spinner(f"Fetching {len(urls)} page(s)…"):
            docs = load_all(urls)
        if not docs:
            st.error("No content could be loaded. Double-check the URLs and try again.")
        else:
            with st.spinner("Chunking and embedding…"):
                chunks = split_documents(docs)
                store_chunks(chunks, get_embeddings())
            st.success(f"✅  {len(urls)} URL(s) ingested successfully — {len(chunks):,} chunks added.")
