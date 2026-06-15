from pathlib import Path
import logging

from dotenv import load_dotenv
from langchain_community.document_loaders import (
    PyPDFLoader,
    Docx2txtLoader,
    TextLoader,
    WebBaseLoader,
)

from config import SUPPORTED_EXTENSIONS, MAX_FILE_SIZE_MB

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_document(source: str):
    if not isinstance(source, str) or not source.strip():
        raise ValueError("Source must be a non-empty string.")

    source = source.strip()

    if source.startswith(("http://", "https://")):
        docs = WebBaseLoader(source).load()

    else:
        path = Path(source)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        if not path.is_file():
            raise ValueError(f"Source is not a file: {path}")

        ext = path.suffix.lower()

        if ext not in SUPPORTED_EXTENSIONS:
            raise ValueError(f"Unsupported file type: {ext}")

        size_mb = path.stat().st_size / (1024 * 1024)

        if size_mb > MAX_FILE_SIZE_MB:
            raise ValueError(f"{path.name} exceeds {MAX_FILE_SIZE_MB} MB limit.")

        if ext == ".pdf":
            docs = PyPDFLoader(str(path)).load()
        elif ext == ".docx":
            docs = Docx2txtLoader(str(path)).load()
        elif ext == ".txt":
            docs = TextLoader(str(path), encoding="utf-8").load()
        else:
            raise ValueError(f"No loader configured for file type: {ext}")

    if not docs:
        raise ValueError(f"No content loaded from: {source}")

    for doc in docs:
        doc.metadata["source"] = source

    logger.info("Loaded %s document(s) from %s", len(docs), source)
    return docs


def load_all(sources: list):
    all_docs = []

    for source in sources:
        try:
            all_docs.extend(load_document(source))
        except Exception as e:
            logger.warning("Skipped '%s': %s", source, e)

    return all_docs