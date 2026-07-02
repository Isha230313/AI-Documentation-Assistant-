import logging
import traceback

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from auth_utils import get_current_user
from embedding import get_embeddings
from vector import get_retriever
from rag import build_chain, ask

logger = logging.getLogger(__name__)

router = APIRouter(tags=["chat"])

# Lazy-initialized singletons — created on first request, reused after.
# The QdrantVectorStore queries Qdrant at call time, so newly ingested
# documents are visible without restarting.
_llm = None
_retriever = None


def _get_llm_and_retriever():
    global _llm, _retriever
    if _llm is None:
        embeddings = get_embeddings()
        _retriever = get_retriever(embeddings)
        _llm = build_chain()
    return _llm, _retriever


class ChatRequest(BaseModel):
    question: str


@router.post("/chat")
async def chat(request: ChatRequest, current_user: dict = Depends(get_current_user)):
    try:
        llm, retriever = _get_llm_and_retriever()
        result = ask(request.question, llm, retriever)
        return result
    except Exception as exc:
        logger.error("Chat error:\n%s", traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(exc))
