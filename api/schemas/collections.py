from pydantic import BaseModel


class CollectionInfo(BaseModel):
    name: str
    vectors: int


class CollectionsResponse(BaseModel):
    total_collections: int
    total_vectors: int
    collections: list[CollectionInfo]
