from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from api.deps import require_admin
from api.schemas.collections import CollectionsResponse

router = APIRouter(prefix="/sources", tags=["Sources"])


def _get_all_sources() -> list[str]:
    """Scroll through all Qdrant points and collect unique source values."""
    from vector import get_client
    from config import COLLECTION_NAME

    client = get_client()
    try:
        existing = [c.name for c in client.get_collections().collections]
        if COLLECTION_NAME not in existing:
            return []

        sources = set()
        offset = None

        while True:
            results, next_offset = client.scroll(
                collection_name=COLLECTION_NAME,
                with_payload=True,
                with_vectors=False,
                limit=100,
                offset=offset,
            )
            for point in results:
                src = point.payload.get("metadata", {}).get("source")
                if src:
                    sources.add(src)

            if next_offset is None:
                break
            offset = next_offset

        return sorted(sources)
    finally:
        client.close()


class DeleteSourceRequest(BaseModel):
    source: str


@router.get("", response_model=list[str])
def list_sources(_admin: dict = Depends(require_admin)):
    """List all unique document sources currently indexed."""
    try:
        return _get_all_sources()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e))


@router.delete("", status_code=200)
def delete_source(body: DeleteSourceRequest, _admin: dict = Depends(require_admin)):
    """Delete all chunks belonging to a specific source (file or URL)."""
    from qdrant_client.models import Filter, FieldCondition, MatchValue
    from vector import get_client
    from config import COLLECTION_NAME

    try:
        client = get_client()
        client.delete(
            collection_name=COLLECTION_NAME,
            points_selector=Filter(
                must=[FieldCondition(key="metadata.source", match=MatchValue(value=body.source))]
            ),
        )
        client.close()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    return {"message": f"Deleted all chunks for source: {body.source}"}
