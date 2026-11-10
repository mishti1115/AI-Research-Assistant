"""
AI Research Paper Assistant — FastAPI application entrypoint.
"""
from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import get_settings
from app.core.logging_config import get_logger, setup_logging
from app.routers import chat, citation, papers, summary

setup_logging()
logger = get_logger(__name__)
settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    description="RAG-powered assistant for chatting with, summarizing, and comparing research papers.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    # Vercel gives every deployment its own unique subdomain (previews,
    # branch deploys, etc.), not just the main project URL — this regex
    # allows any *.vercel.app origin so CORS doesn't break on those without
    # having to list every deployment URL individually.
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(papers.router)
app.include_router(chat.router)
app.include_router(summary.router)
app.include_router(citation.router)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    """Catch-all so unexpected errors return a clean JSON response, not a stack trace."""
    logger.exception("Unhandled exception on %s %s", request.method, request.url.path)
    return JSONResponse(status_code=500, content={"detail": "Internal server error."})


@app.get("/health", tags=["system"])
async def health_check():
    return {"status": "ok", "app": settings.APP_NAME, "environment": settings.ENVIRONMENT}


@app.get("/", tags=["system"])
async def root():
    return {
        "message": f"{settings.APP_NAME} API is running.",
        "docs": "/docs",
    }
