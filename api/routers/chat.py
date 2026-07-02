from fastapi import APIRouter, Depends, HTTPException, status

from api.deps import get_current_user
from api.schemas.chat import ChatRequest, ChatResponse

router = APIRouter(prefix="/chat", tags=["Chat"])

# Initialized once on first request, reused for all subsequent calls
_rag_cache: dict = {}


def _get_rag():
    if not _rag_cache:
        from embedding import get_embeddings
        from vector import get_retriever
        from rag import build_chain

        embeddings = get_embeddings()
        retriever  = get_retriever(embeddings)
        _rag_cache["retriever"] = retriever
        _rag_cache["llm"]       = build_chain()

    return _rag_cache["retriever"], _rag_cache["llm"]


@router.post("", response_model=ChatResponse)
def chat(body: ChatRequest, _user: dict = Depends(get_current_user)):
    try:
        from rag import ask
        retriever, llm = _get_rag()
        result = ask(body.question, llm, retriever)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    return ChatResponse(answer=result["answer"], sources=result["sources"])
