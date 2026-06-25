from pydantic import BaseModel, HttpUrl


class UrlIngestRequest(BaseModel):
    urls: list[HttpUrl]


class IngestResponse(BaseModel):
    message: str
    chunks_added: int
