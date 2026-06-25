import os
import tempfile

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status

from api.deps import require_admin
from api.schemas.ingest import IngestResponse, UrlIngestRequest

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt"}
MAX_FILE_SIZE_MB   = 50

router = APIRouter(prefix="/ingest", tags=["Ingest"])


def _run_pipeline(docs) -> int:
    """Chunk → embed → store. Returns number of chunks added."""
    from chunking import split_documents
    from embedding import get_embeddings
    from vector import store_chunks

    chunks = split_documents(docs)
    store_chunks(chunks, get_embeddings())
    return len(chunks)


@router.post("/files", response_model=IngestResponse, status_code=201)
async def ingest_files(
    files: list[UploadFile] = File(...),
    _admin: dict = Depends(require_admin),
):
    from ingest import load_document

    if not files:
        raise HTTPException(status_code=400, detail="No files provided.")

    total_chunks = 0
    errors: list[str] = []

    for upload in files:
        ext = os.path.splitext(upload.filename)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            errors.append(f"{upload.filename}: unsupported type '{ext}'.")
            continue

        content = await upload.read()
        if len(content) > MAX_FILE_SIZE_MB * 1024 * 1024:
            errors.append(f"{upload.filename}: exceeds {MAX_FILE_SIZE_MB} MB limit.")
            continue

        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
            tmp.write(content)
            tmp_path = tmp.name

        try:
            docs = load_document(tmp_path)
            for doc in docs:
                doc.metadata["source"] = upload.filename
            total_chunks += _run_pipeline(docs)
        except Exception as e:
            errors.append(f"{upload.filename}: {e}")
        finally:
            os.unlink(tmp_path)

    if errors and total_chunks == 0:
        raise HTTPException(status_code=422, detail=errors)

    msg = f"{len(files)} file(s) ingested."
    if errors:
        msg += f" Warnings: {errors}"

    return IngestResponse(message=msg, chunks_added=total_chunks)


@router.post("/urls", response_model=IngestResponse, status_code=201)
def ingest_urls(body: UrlIngestRequest, _admin: dict = Depends(require_admin)):
    from ingest import load_all

    urls = [str(u) for u in body.urls]
    if not urls:
        raise HTTPException(status_code=400, detail="No URLs provided.")

    docs = load_all(urls)
    if not docs:
        raise HTTPException(status_code=422, detail="No content could be loaded. Check the URLs and try again.")

    return IngestResponse(message=f"{len(urls)} URL(s) ingested.", chunks_added=_run_pipeline(docs))
