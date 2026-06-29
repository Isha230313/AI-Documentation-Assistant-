from fastapi import APIRouter, Depends

from auth_utils import get_current_user
from vector import get_client

router = APIRouter(tags=["collections"])


@router.get("/collections")
async def get_collections(current_user: dict = Depends(get_current_user)):
    client = get_client()
    try:
        cols = client.get_collections().collections
        result = []
        total_vectors = 0
        for col in cols:
            count = client.get_collection(col.name).points_count or 0
            result.append({"name": col.name, "vectors": count})
            total_vectors += count
        return {
            "total_collections": len(result),
            "total_vectors": total_vectors,
            "collections": result,
        }
    finally:
        client.close()
