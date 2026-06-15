# app/main.py
from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router as api_router
from app.core.config import get_settings

settings = get_settings()
logger = logging.getLogger("lexcare-ai")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting %s", settings.app_name)
    yield
    logger.info("Shutting down %s", settings.app_name)


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        description="RAG-based assistant for healthcare regulations, legislation, and policy updates.",
        version="0.1.0",
        lifespan=lifespan,
        docs_url=None,
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.parsed_cors_origins(),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router, prefix="/api")

    @app.get("/", summary="Root endpoint")
    async def root() -> dict[str, str]:
        return {"message": f"{settings.app_name} is running", "status": "ok"}

    @app.get("/health", summary="Health check")
    async def health() -> dict[str, str]:
        return {"status": "healthy"}

    return app


app = create_app()
