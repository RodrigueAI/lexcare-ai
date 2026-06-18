# app/services/vectorstore_service.py
from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from langchain_community.vectorstores.chroma import Chroma
from langchain_core.documents import Document

from app.core.config import Settings, get_settings
from app.domain.models import DocumentChunk, DocumentMetadata
from app.services.embedding_service import EmbeddingService


class VectorStoreService:
    def __init__(
        self,
        settings: Settings | None = None,
        embedding_service: EmbeddingService | None = None,
        collection_name: str = "lexcare_ai",
    ) -> None:
        self.settings = settings or get_settings()
        self.embedding_service = embedding_service or EmbeddingService(self.settings)

        self._store = Chroma(
            collection_name=collection_name,
            persist_directory=self.settings.chroma_path,
            embedding_function=self.embedding_service.embedding_function,
        )

    def add_chunks(self, chunks: list[DocumentChunk], batch_size: int = 100) -> None:
        if not chunks:
            return

        if batch_size <= 0:
            raise ValueError("batch_size must be greater than 0")

        for start in range(0, len(chunks), batch_size):
            batch = chunks[start : start + batch_size]

            texts = [chunk.text for chunk in batch]
            metadatas = [self._chunk_to_metadata(chunk) for chunk in batch]
            ids = [chunk.chunk_id for chunk in batch]

            self._store.add_texts(texts=texts, metadatas=metadatas, ids=ids)

    def similarity_search(self, query: str, top_k: int = 5) -> list[DocumentChunk]:
        docs = self._store.similarity_search(query, k=top_k)
        return [self._document_to_chunk(doc) for doc in docs]

    def _chunk_to_metadata(self, chunk: DocumentChunk) -> dict[str, Any]:
        metadata = chunk.metadata.to_dict()

        return {
            "document_id": chunk.document_id,
            "chunk_id": chunk.chunk_id,
            "chunk_index": chunk.chunk_index,
            "source_path": chunk.source_path,
            "source": metadata["source"],
            "document_type": metadata["document_type"],
            "topic": metadata["topic"],
            "created_at": metadata["created_at"],
            "extra_json": json.dumps(metadata["extra"], ensure_ascii=False, default=str),
        }

    def _document_to_chunk(self, doc: Document) -> DocumentChunk:
        metadata = doc.metadata

        created_at_raw = metadata.get("created_at")
        if isinstance(created_at_raw, str):
            created_at = datetime.fromisoformat(created_at_raw)
        else:
            created_at = datetime.now(timezone.utc)

        chunk_metadata = DocumentMetadata(
            source=metadata["source"],
            document_type=metadata["document_type"],
            topic=metadata["topic"],
            created_at=created_at,
            extra=json.loads(metadata.get("extra_json", "{}")),
        )

        return DocumentChunk(
            document_id=metadata["document_id"],
            chunk_id=metadata["chunk_id"],
            chunk_index=int(metadata["chunk_index"]),
            source_path=metadata["source_path"],
            text=doc.page_content,
            metadata=chunk_metadata,
        )