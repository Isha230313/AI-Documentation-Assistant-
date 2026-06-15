    



import sys
import os
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from ingest import load_document, load_all
from chunking import split_documents
from embedding import get_embeddings
from vector import store_chunks, get_retriever, get_client
from rag import build_chain, ask

# ── Page config ──────────────────────────────────────────────
st.set_page_config(
    page_title="AI Documentation Assistant",
    page_icon="📚",
    layout="wide",
)

st.markdown("""
<style>
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stHeader"] { display: none; }
[data-testid="stSidebarNav"] { display: none; }
[data-testid="stNavLink"] { display: none; }
</style>
""", unsafe_allow_html=True)

st.title("📚 AI Documentation Assistant")
st.caption("Ingest documents, then ask questions — answers are grounded in your docs.")

# ── Cached resources (rebuilt once per session) ───────────────
@st.cache_resource(show_spinner=False)
def load_rag():
    embeddings = get_embeddings()
    retriever  = get_retriever(embeddings)
    chain      = build_chain(retriever)
    return embeddings, retriever, chain

# ── Sidebar — Ingest ──────────────────────────────────────────
with st.sidebar:
    st.header("Ingest Documents")

    # --- URL ingestion ---
    st.subheader("From URL")
    url_input = st.text_area(
        "Paste URLs (one per line)",
        height=120,
        placeholder="https://docs.python.org/3/library/functions.html",
    )
    if st.button("Ingest URLs", use_container_width=True):
        urls = [u.strip() for u in url_input.splitlines() if u.strip()]
        if not urls:
            st.warning("Enter at least one URL.")
        else:
            with st.spinner(f"Loading {len(urls)} URL(s)…"):
                docs = load_all(urls)
            if not docs:
                st.error("No content loaded. Check the URLs.")
            else:
                with st.spinner("Chunking and embedding…"):
                    chunks    = split_documents(docs)
                    embeddings, _, _ = load_rag()
                    store_chunks(chunks, embeddings)
                    load_rag.clear()          # force retriever rebuild
                st.success(f"Stored {len(chunks)} chunks from {len(docs)} page(s).")

    st.divider()

    # --- File upload ---
    st.subheader("From File")
    uploaded_files = st.file_uploader(
        "Upload PDF, DOCX, or TXT",
        type=["pdf", "docx", "txt"],
        accept_multiple_files=True,
    )
    if st.button("Ingest Files", use_container_width=True):
        if not uploaded_files:
            st.warning("Upload at least one file.")
        else:
            all_chunks = []
            for f in uploaded_files:
                suffix = os.path.splitext(f.name)[1]
                with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                    tmp.write(f.read())
                    tmp_path = tmp.name
                try:
                    with st.spinner(f"Loading {f.name}…"):
                        docs   = load_document(tmp_path)
                        for doc in docs:
                            doc.metadata["source"] = f.name
                        chunks = split_documents(docs)
                        all_chunks.extend(chunks)
                except Exception as e:
                    st.error(f"{f.name}: {e}")
                finally:
                    os.unlink(tmp_path)

            if all_chunks:
                with st.spinner("Embedding and storing…"):
                    embeddings, _, _ = load_rag()
                    store_chunks(all_chunks, embeddings)
                    load_rag.clear()
                st.success(f"Stored {len(all_chunks)} chunks from {len(uploaded_files)} file(s).")

    st.divider()

    # --- Collection stats ---
    st.subheader("Vector Store")
    try:
        client = get_client()
        for col in client.get_collections().collections:
            count = client.get_collection(col.name).points_count
            st.metric(col.name, f"{count} vectors")
        client.close()
    except Exception as e:
        st.warning(f"Could not read stats: {e}")

# ── Chat ──────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("sources"):
            with st.expander("Sources"):
                for src in msg["sources"]:
                    st.markdown(f"- {src}")

question = st.chat_input("Ask a question about your documents…")

if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Thinking…"):
            _, retriever, chain = load_rag()
            response = ask(question, chain, retriever)

        st.markdown(response["answer"])
        if response["sources"]:
            with st.expander("Sources"):
                for src in response["sources"]:
                    st.markdown(f"- {src}")

    st.session_state.messages.append({
        "role":    "assistant",
        "content": response["answer"],
        "sources": response["sources"],
    })
