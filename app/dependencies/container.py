# app/dependencies/container.py
from app.core.config import Settings, get_settings
from app.services.rag_service import RAGService


def get_rag_service() -> RAGService:
    return RAGService()


def get_app_settings() -> Settings:
    return get_settings()