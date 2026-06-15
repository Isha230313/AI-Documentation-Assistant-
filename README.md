# AI Documentation Assistant

A domain-specific RAG-based documentation assistant. Upload any document and ask questions about it.

**Stack:** Python · LangChain · OpenAI Embeddings · Qdrant · Claude

---

## Project Structure

```
AI Documentation Assistant/
├── src/
│   ├── config.py       # All settings
│   ├── ingest.py       # Load & index documents
│   ├── chunking.py     # Split documents into chunks
│   ├── embedding.py    # OpenAI embeddings
│   ├── vector.py       # Qdrant vector store & retriever
│   └── rag.py          # RAG chain & chat
├── data/raw/           # Place your documents here
├── qdrant_storage/     # Persistent vector database (auto-created)
├── requirements.txt
└── README.md
```

---

## Setup

**1. Clone the repo and install dependencies**
```bash
pip install -r requirements.txt
```

**2. Create a `.env` file in the root folder**
```
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
```

---

## Usage

**Step 1 — Ingest your documents**

Add your file paths or URLs to `SOURCES` in `src/ingest.py`, then run:
```bash
cd src
python ingest.py
```

Supported sources:
- PDF files: `./data/raw/my_doc.pdf`
- DOCX files: `./data/raw/report.docx`
- TXT files: `./data/raw/notes.txt`
- Web URLs: `https://docs.python.org/3/library/functions.html`

**Step 2 — Start chatting**
```bash
python rag.py
```

---

## Configuration

All settings are in `src/config.py`:

| Setting | Default | Description |
|---|---|---|
| `EMBEDDING_MODEL` | `text-embedding-3-small` | OpenAI embedding model |
| `ANTHROPIC_MODEL` | `claude-opus-4-6` | Claude model |
| `CHUNK_SIZE` | `800` | Characters per chunk |
| `CHUNK_OVERLAP` | `100` | Overlap between chunks |
| `RETRIEVER_K` | `5` | Chunks retrieved per query |
| `COLLECTION_NAME` | `docs_general` | Qdrant collection name |

---

## Roadmap

- Streamlit UI with file upload
- Multi-domain support
- Chat history
- Hybrid search (dense + sparse)
