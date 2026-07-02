import os

# Embedding
EMBEDDING_MODEL      = "text-embedding-3-small"
EMBEDDING_DIMENSIONS = 1536

# LLM
ANTHROPIC_MODEL = "claude-opus-4-6"
TEMPERATURE     = 0.3
MAX_TOKENS      = 2048

# Chunking
CHUNK_SIZE    = 800
CHUNK_OVERLAP = 100

# Retrieval
RETRIEVER_K              = 5
RETRIEVER_SEARCH_TYPE    = "similarity_score_threshold"
RETRIEVER_SCORE_THRESHOLD = 0.72

# Qdrant
QDRANT_URL      = os.getenv("QDRANT_URL", "http://localhost:6333")
QDRANT_API_KEY  = os.getenv("QDRANT_API_KEY", None)
COLLECTION_NAME = "docs_general"

# File handling
SUPPORTED_EXTENSIONS = [".pdf", ".docx", ".txt"]
MAX_FILE_SIZE_MB     = 50
