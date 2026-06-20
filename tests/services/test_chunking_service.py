from __future__ import annotations

from datetime import UTC, datetime

import pytest

from app.domain.models import DocumentMetadata, StoredDocument
from app.services.chunking_service import ChunkingService


def _make_stored_document(text: str) -> StoredDocument:
    metadata = DocumentMetadata(
        source="gesetze-im-internet",
        document_type="law",
        topic="krankenversicherung",
        created_at=datetime(2024, 1, 1, tzinfo=UTC),
        extra={
            "filename": "SGB_5.pdf",
            "page_count": 568,
            "file_size_bytes": 123456,
        },
    )

    return StoredDocument(
        document_id="doc-1",
        source_path="data/raw/gesetze_im_internet/SGB_5.pdf",
        text=text,
        metadata=metadata,
    )


def test_chunking_splits_text_into_multiple_chunks() -> None:
    document = _make_stored_document("a" * 2500)
    service = ChunkingService(chunk_size=1000, chunk_overlap=200)

    chunks = service.split(document)

    assert len(chunks) == 3
    assert chunks[0].chunk_index == 0
    assert chunks[1].chunk_index == 1
    assert chunks[2].chunk_index == 2
    assert chunks[0].document_id == "doc-1"


def test_chunking_generates_chunk_ids() -> None:
    document = _make_stored_document("a" * 1200)
    service = ChunkingService(chunk_size=1000, chunk_overlap=200)

    chunks = service.split(document)

    assert chunks[0].chunk_id == "doc-1-chunk-0000"
    assert chunks[1].chunk_id == "doc-1-chunk-0001"


def test_chunking_preserves_metadata() -> None:
    document = _make_stored_document("a" * 1200)
    service = ChunkingService(chunk_size=1000, chunk_overlap=200)

    chunks = service.split(document)

    assert len(chunks) > 0
    assert chunks[0].metadata == document.metadata
    assert chunks[0].metadata.source == "gesetze-im-internet"
    assert chunks[0].metadata.document_type == "law"
    assert chunks[0].metadata.topic == "krankenversicherung"


def test_chunking_returns_empty_list_for_empty_text() -> None:
    document = _make_stored_document("")
    service = ChunkingService(chunk_size=1000, chunk_overlap=200)

    chunks = service.split(document)

    assert chunks == []


def test_chunking_uses_override_text_when_provided() -> None:
    document = _make_stored_document("a" * 50)
    service = ChunkingService(chunk_size=20, chunk_overlap=5)

    chunks = service.split(document, text="b" * 55)

    assert len(chunks) == 4
    assert all("b" in chunk.text for chunk in chunks)


@pytest.mark.parametrize(
    "chunk_size,chunk_overlap,error_message",
    [
        (0, 100, "chunk_size must be greater than 0"),
        (1000, -1, "chunk_overlap must not be negative"),
        (100, 100, "chunk_overlap must be smaller than chunk_size"),
        (100, 150, "chunk_overlap must be smaller than chunk_size"),
    ],
)
def test_chunking_rejects_invalid_configuration(
    chunk_size: int,
    chunk_overlap: int,
    error_message: str,
) -> None:
    with pytest.raises(ValueError, match=error_message):
        ChunkingService(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
