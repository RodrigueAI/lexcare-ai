# src/app/services/chunking_service.py
from dataclasses import replace

from app.domain.models import DocumentChunk, StoredDocument


class ChunkingService:
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200) -> None:
        if chunk_size <= 0:
            raise ValueError("chunk_size must be greater than 0")
        if chunk_overlap < 0:
            raise ValueError("chunk_overlap must not be negative")
        if chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap must be smaller than chunk_size")

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split(self, document: StoredDocument, text: str | None = None) -> list[DocumentChunk]:
        content = (text if text is not None else document.text).strip()

        if not content:
            return []

        chunks: list[DocumentChunk] = []
        start = 0
        chunk_index = 0
        total_length = len(content)

        while start < total_length:
            end = min(start + self.chunk_size, total_length)
            chunk_text = content[start:end].strip()

            if chunk_text:
                chunks.append(
                    DocumentChunk(
                        document_id=document.document_id,
                        chunk_id=f"{document.document_id}-chunk-{chunk_index:04d}",
                        chunk_index=chunk_index,
                        source_path=document.source_path,
                        text=chunk_text,
                        metadata=replace(document.metadata),
                    )
                )
                chunk_index += 1

            if end >= total_length:
                break

            start = max(end - self.chunk_overlap, start + 1)

        return chunks