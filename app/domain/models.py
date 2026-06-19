# app/domain/models.py
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any


@dataclass(frozen=True)
class DocumentMetadata:
    source: str
    document_type: str
    topic: str
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    extra: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "source": self.source,
            "document_type": self.document_type,
            "topic": self.topic,
            "created_at": self.created_at.isoformat(),
            "extra": self.extra,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> DocumentMetadata:
        created_at_raw = data.get("created_at")
        created_at = (
            datetime.fromisoformat(created_at_raw)
            if isinstance(created_at_raw, str)
            else datetime.now(UTC)
        )

        return cls(
            source=data["source"],
            document_type=data["document_type"],
            topic=data["topic"],
            created_at=created_at,
            extra=data.get("extra", {}),
        )


@dataclass(frozen=True)
class LoadedDocument:
    source_path: str
    text: str
    metadata: DocumentMetadata

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_path": self.source_path,
            "text": self.text,
            "metadata": self.metadata.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> LoadedDocument:
        return cls(
            source_path=data["source_path"],
            text=data["text"],
            metadata=DocumentMetadata.from_dict(data["metadata"]),
        )


@dataclass(frozen=True)
class StoredDocument:
    document_id: str
    source_path: str
    text: str
    metadata: DocumentMetadata

    def to_dict(self) -> dict[str, Any]:
        return {
            "document_id": self.document_id,
            "source_path": self.source_path,
            "text": self.text,
            "metadata": self.metadata.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> StoredDocument:
        return cls(
            document_id=data["document_id"],
            source_path=data["source_path"],
            text=data["text"],
            metadata=DocumentMetadata.from_dict(data["metadata"]),
        )


@dataclass(frozen=True)
class DocumentChunk:
    document_id: str
    chunk_id: str
    chunk_index: int
    source_path: str
    text: str
    metadata: DocumentMetadata

    def to_dict(self) -> dict[str, Any]:
        return {
            "document_id": self.document_id,
            "chunk_id": self.chunk_id,
            "chunk_index": self.chunk_index,
            "source_path": self.source_path,
            "text": self.text,
            "metadata": self.metadata.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> DocumentChunk:
        return cls(
            document_id=data["document_id"],
            chunk_id=data["chunk_id"],
            chunk_index=data["chunk_index"],
            source_path=data["source_path"],
            text=data["text"],
            metadata=DocumentMetadata.from_dict(data["metadata"]),
        )


@dataclass(frozen=True)
class GeneratedAnswer:
    question: str
    answer: str
    sources: list[dict[str, Any]] = field(default_factory=list)
