import hashlib
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from langchain_qdrant import QdrantVectorStore
from config import QDRANT_URL, QDRANT_API_KEY, COLLECTION_NAME, EMBEDDING_DIMENSIONS, RETRIEVER_K, RETRIEVER_SEARCH_TYPE, RETRIEVER_SCORE_THRESHOLD


def get_client():
    return QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)


def ensure_collection(client):
    existing = [c.name for c in client.get_collections().collections]
    if COLLECTION_NAME not in existing:
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=EMBEDDING_DIMENSIONS, distance=Distance.COSINE),
        )
        print(f"Created collection: {COLLECTION_NAME}")
    else:
        count = client.get_collection(COLLECTION_NAME).points_count
        print(f"Collection '{COLLECTION_NAME}' exists ({count} vectors).")


def get_chunk_ids(chunks):
    return [
        hashlib.md5(f"{c.metadata.get('source', '')}_{i}".encode()).hexdigest()
        for i, c in enumerate(chunks)
    ]


def store_chunks(chunks, embeddings):
    client = get_client()
    ensure_collection(client)

    ids          = get_chunk_ids(chunks)
    vector_store = QdrantVectorStore(client=client, collection_name=COLLECTION_NAME, embedding=embeddings)
    vector_store.add_documents(documents=chunks, ids=ids)

    total = client.get_collection(COLLECTION_NAME).points_count
    print(f"Stored. Total vectors: {total}")


def get_retriever(embeddings):
    client = get_client()
    ensure_collection(client)
    vector_store = QdrantVectorStore(client=client, collection_name=COLLECTION_NAME, embedding=embeddings)
    return vector_store.as_retriever(
        search_type=RETRIEVER_SEARCH_TYPE,
        search_kwargs={"k": RETRIEVER_K, "score_threshold": RETRIEVER_SCORE_THRESHOLD},
    )
