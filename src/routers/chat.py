from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from auth_utils import get_current_user
from embedding import get_embeddings
from vector import get_retriever
from rag import build_chain, ask

router = APIRouter(tags=["chat"])

# Lazy-initialized singletons — created on first request, reused after.
# The QdrantVectorStore queries Qdrant at call time, so newly ingested
# documents are visible without restarting.
_chain = None
_retriever = None


def _get_chain_and_retriever():
    global _chain, _retriever
    if _chain is None:
        embeddings = get_embeddings()
        _retriever = get_retriever(embeddings)
        _chain = build_chain(_retriever)
    return _chain, _retriever


class ChatRequest(BaseModel):
    question: str


@router.post("/chat")
async def chat(request: ChatRequest, current_user: dict = Depends(get_current_user)):
    try:
        chain, retriever = _get_chain_and_retriever()
        result = ask(request.question, chain, retriever)
        return result
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
