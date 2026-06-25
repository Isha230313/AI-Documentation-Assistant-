from fastapi import APIRouter, Depends, HTTPException, status

from api.deps import get_current_user
from api.schemas.collections import CollectionInfo, CollectionsResponse

router = APIRouter(prefix="/collections", tags=["Collections"])


@router.get("", response_model=CollectionsResponse)
def get_collections(_user: dict = Depends(get_current_user)):
    from vector import get_client

    try:
        client = get_client()
        raw    = client.get_collections().collections

        collections = []
        total_vectors = 0
        for col in raw:
            count = client.get_collection(col.name).points_count or 0
            total_vectors += count
            collections.append(CollectionInfo(name=col.name, vectors=count))

        client.close()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e))

    return CollectionsResponse(
        total_collections=len(collections),
        total_vectors=total_vectors,
        collections=collections,
    )
