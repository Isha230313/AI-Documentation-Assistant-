import sys
import os

# Make src/ importable from anywhere — done once here, not repeated in every router
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "src"))

from contextlib import asynccontextmanager
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.core.config import settings
from api.routers import auth, chat, collections, ingest, sources
from api.users_store import bootstrap_admin


@asynccontextmanager
async def lifespan(app: FastAPI):
    bootstrap_admin()
    print(f"[startup] {settings.PROJECT_NAME} API is ready.")
    yield
    print("[shutdown] Goodbye.")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

prefix = settings.API_V1_PREFIX
app.include_router(auth.router,        prefix=prefix)
app.include_router(chat.router,        prefix=prefix)
app.include_router(ingest.router,      prefix=prefix)
app.include_router(collections.router, prefix=prefix)
app.include_router(sources.router,     prefix=prefix)


@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok"}
