# app/services/retriever_service.py
from __future__ import annotations

from app.domain.models import DocumentChunk
from app.services.vectorstore_service import VectorStoreService


class RetrieverService:
    def __init__(self, vectorstore_service: VectorStoreService | None = None) -> None:
        self.vectorstore_service = vectorstore_service or VectorStoreService()

    def retrieve(self, query: str, top_k: int = 5) -> list[DocumentChunk]:
        if not query or not query.strip():
            return []

        if top_k <= 0:
            raise ValueError("top_k must be greater than 0")

        return self.vectorstore_service.similarity_search(query=query, top_k=top_k)
