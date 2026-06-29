import os
import sys

# Make src/ importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers.auth import router as auth_router
from routers.chat import router as chat_router
from routers.collections import router as collections_router
from routers.ingest import router as ingest_router
from routers.sources import router as sources_router

app = FastAPI(title="AI Documentation Assistant API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

PREFIX = "/api/v1"

app.include_router(auth_router, prefix=PREFIX)
app.include_router(chat_router, prefix=PREFIX)
app.include_router(ingest_router, prefix=PREFIX)
app.include_router(collections_router, prefix=PREFIX)
app.include_router(sources_router, prefix=PREFIX)


@app.get("/health")
def health():
    return {"status": "ok"}
