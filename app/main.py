from contextlib import asynccontextmanager
import logging
import os
from typing import Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

try:
    from app.api.routes import router as api_router
except ImportError:
    api_router = None


logger = logging.getLogger("lexcare-ai")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting LexCare AI application")
    yield
    logger.info("Shutting down LexCare AI application")


def create_app() -> FastAPI:
    app = FastAPI(
        title="LexCare AI",
        description="RAG-based assistant for healthcare regulations, legislation, and policy updates.",
        version="0.1.0",
        lifespan=lifespan,
    )

    cors_origins = os.getenv("CORS_ORIGINS", "*")
    allowed_origins = [origin.strip() for origin in cors_origins.split(",")] if cors_origins else ["*"]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    if api_router is not None:
        app.include_router(api_router, prefix="/api", tags=["API"])

    @app.get("/", summary="Root endpoint")
    async def root() -> dict[str, str]:
        return {
            "message": "LexCare AI is running",
            "status": "ok",
        }

    @app.get("/health", summary="Health check")
    async def health() -> dict[str, str]:
        return {
            "status": "healthy",
        }

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "8000")),
        reload=os.getenv("RELOAD", "true").lower() == "true",
    )