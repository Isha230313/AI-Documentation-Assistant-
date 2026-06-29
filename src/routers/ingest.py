import os
import tempfile
from typing import List

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel

from auth_utils import get_current_user
from chunking import split_documents
from embedding import get_embeddings
from ingest import load_all, load_document
from vector import store_chunks

router = APIRouter(prefix="/ingest", tags=["ingest"])


@router.post("/files")
async def ingest_files(
    files: List[UploadFile] = File(...),
    current_user: dict = Depends(get_current_user),
):
    embeddings = get_embeddings()
    all_chunks = []
    errors = []

    for upload in files:
        suffix = os.path.splitext(upload.filename or "")[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(await upload.read())
            tmp_path = tmp.name
        try:
            docs = load_document(tmp_path)
            for doc in docs:
                doc.metadata["source"] = upload.filename
            all_chunks.extend(split_documents(docs))
        except Exception as exc:
            errors.append(f"{upload.filename}: {exc}")
        finally:
            os.unlink(tmp_path)

    if errors and not all_chunks:
        raise HTTPException(status_code=400, detail="; ".join(errors))

    store_chunks(all_chunks, embeddings)
    return {"message": f"{len(files)} file(s) ingested", "chunks_added": len(all_chunks)}


class UrlsRequest(BaseModel):
    urls: List[str]


@router.post("/urls")
async def ingest_urls(
    request: UrlsRequest,
    current_user: dict = Depends(get_current_user),
):
    if not request.urls:
        raise HTTPException(status_code=400, detail="No URLs provided.")

    embeddings = get_embeddings()
    docs = load_all(request.urls)

    if not docs:
        raise HTTPException(
            status_code=400,
            detail="No content could be loaded from the provided URLs.",
        )

    chunks = split_documents(docs)
    store_chunks(chunks, embeddings)
    return {"message": f"{len(request.urls)} URL(s) ingested", "chunks_added": len(chunks)}
