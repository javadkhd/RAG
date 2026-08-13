from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.middleware import (
    ErrorHandlingMiddleware,
    RateLimitMiddleware,
    RequestIdMiddleware,
    RequestLoggingMiddleware,
    SecurityHeadersMiddleware,
)
from app.api.routers.chat import router as chat_router
from app.api.routers.conversations import router as conversations_router
from app.api.routers.datasets import router as datasets_router
from app.api.routers.ingestion import router as ingestion_router
from app.api.routers.tasks import router as tasks_router
from app.api.routers.workspaces import router as workspaces_router
from app.config import settings
from app.db.session import db
from app.logging_config import setup_logging
from app.providers.embeddings import get_embedding_provider
from app.providers.llm import get_llm_provider
from app.providers.vectordb import PgVectorStore
from app.retrieval.retrievers.bm25 import BM25Retriever
from app.retrieval.retrievers.dense import DenseRetriever
from app.retrieval.retrievers.hybrid import HybridRetriever
from app.services.chat import ChatService

setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    db.init()
    yield
    await db.dispose()


app = FastAPI(
    title=settings.app.name,
    version=settings.app.version,
    description="Production-ready modular RAG Platform",
    debug=settings.app.debug,
    lifespan=lifespan,
)

app.add_middleware(ErrorHandlingMiddleware)
app.add_middleware(RateLimitMiddleware, max_requests=100, window_seconds=60)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(RequestIdMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["Health"])
async def health() -> dict[str, str]:
    return {"status": "ok", "version": settings.app.version}


@app.get("/health/ready", tags=["Health"])
async def health_ready() -> JSONResponse:
    deps: dict[str, str] = {}

    db_status = await _check_database()
    deps["postgres"] = db_status

    ollama_status = await _check_ollama()
    deps["ollama"] = ollama_status

    embedding_status = _check_embedding()
    deps["embedding"] = embedding_status

    ready = all(s in ("ok", "configured") for s in deps.values())
    status = "ready" if ready else "degraded"
    payload = {"status": status, "dependencies": deps}
    return JSONResponse(content=payload, status_code=200 if ready else 503)


async def _check_database() -> str:
    try:
        if db.engine is None:
            return "unavailable"
        async with db.engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return "ok"
    except Exception:
        return "error"


async def _check_ollama() -> str:
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            response = await client.get(f"{settings.llm.base_url}/api/tags")
            if response.status_code == 200:
                return "ok"
            return "error"
    except Exception:
        return "error"


def _check_embedding() -> str:
    try:
        import app.providers.embeddings as emb_module

        if getattr(emb_module, "_cached_provider", None) is not None:
            return "ok"
        return "configured"
    except Exception:
        return "error"


@app.get("/", tags=["Root"])
async def root() -> dict[str, str]:
    return {"message": f"Welcome to {settings.app.name}", "version": settings.app.version}


def chat_service_factory(db: AsyncSession) -> ChatService:
    embedding_provider = get_embedding_provider()
    llm_provider = get_llm_provider()
    vector_store = PgVectorStore(session=db)
    dense_retriever = DenseRetriever(db, embedding_provider, vector_store)
    bm25_retriever = BM25Retriever(db)
    hybrid_retriever = HybridRetriever(dense_retriever, bm25_retriever)
    return ChatService(
        session=db,
        llm_provider=llm_provider,
        retriever=hybrid_retriever,
    )


app.state.chat_service_factory = chat_service_factory

app.include_router(workspaces_router)
app.include_router(datasets_router)
app.include_router(ingestion_router)
app.include_router(chat_router)
app.include_router(conversations_router)
app.include_router(tasks_router)
