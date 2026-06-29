from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from qdrant_client.models import FieldCondition, Filter, MatchValue

from auth_utils import get_current_user
from config import COLLECTION_NAME
from vector import get_client

router = APIRouter(prefix="/sources", tags=["sources"])


@router.get("")
async def list_sources(current_user: dict = Depends(get_current_user)):
    client = get_client()
    try:
        sources: set[str] = set()
        offset = None
        while True:
            points, offset = client.scroll(
                collection_name=COLLECTION_NAME,
                limit=100,
                offset=offset,
                with_payload=True,
                with_vectors=False,
            )
            for point in points:
                src = (point.payload or {}).get("metadata", {}).get("source")
                if src:
                    sources.add(src)
            if offset is None:
                break
        return sorted(sources)
    except Exception:
        return []
    finally:
        client.close()


class DeleteRequest(BaseModel):
    source: str


@router.delete("")
async def delete_source(
    request: DeleteRequest,
    current_user: dict = Depends(get_current_user),
):
    client = get_client()
    try:
        client.delete(
            collection_name=COLLECTION_NAME,
            points_selector=Filter(
                must=[FieldCondition(key="metadata.source", match=MatchValue(value=request.source))]
            ),
        )
        return {"message": f"Source '{request.source}' deleted."}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    finally:
        client.close()
