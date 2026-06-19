# app/dependencies/container.py
from functools import lru_cache

from app.core.config import Settings, get_settings
from app.services.embedding_service import EmbeddingService
from app.services.rag_service import RAGService
from app.services.vectorstore_service import VectorStoreService


@lru_cache
def get_app_settings() -> Settings:
    return get_settings()


@lru_cache
def get_embedding_service() -> EmbeddingService:
    return EmbeddingService()


@lru_cache
def get_vectorstore_service() -> VectorStoreService:
    return VectorStoreService()


@lru_cache
def get_rag_service() -> RAGService:
    return RAGService()
