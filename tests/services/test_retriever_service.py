from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import Mock

import pytest

from app.domain.models import DocumentChunk, DocumentMetadata
from app.services.retriever_service import RetrieverService


def _make_chunk() -> DocumentChunk:
    metadata = DocumentMetadata(
        source="gesetze-im-internet",
        document_type="law",
        topic="pflegeversicherung",
        created_at=datetime(2024, 1, 1, tzinfo=UTC),
    )

    return DocumentChunk(
        document_id="doc-1",
        chunk_id="chunk-1",
        chunk_index=0,
        source_path="data/raw/gesetze_im_internet/SGB_11.pdf",
        text="Pflegegrad 3 bedeutet schwere Beeinträchtigungen.",
        metadata=metadata,
    )


def test_retrieve_delegates_to_vectorstore() -> None:
    vectorstore_service = Mock()

    chunks = [_make_chunk(), _make_chunk()]
    vectorstore_service.similarity_search.return_value = chunks

    service = RetrieverService(
        vectorstore_service=vectorstore_service,
    )

    result = service.retrieve(
        "Was ist Pflegegrad 3?",
        top_k=5,
    )

    assert result == chunks

    vectorstore_service.similarity_search.assert_called_once_with(
        query="Was ist Pflegegrad 3?",
        top_k=5,
    )


def test_retrieve_returns_empty_list_for_empty_query() -> None:
    vectorstore_service = Mock()

    service = RetrieverService(
        vectorstore_service=vectorstore_service,
    )

    assert service.retrieve("") == []
    assert service.retrieve("   ") == []

    vectorstore_service.similarity_search.assert_not_called()


def test_retrieve_rejects_invalid_top_k() -> None:
    vectorstore_service = Mock()

    service = RetrieverService(
        vectorstore_service=vectorstore_service,
    )

    with pytest.raises(
        ValueError,
        match="top_k must be greater than 0",
    ):
        service.retrieve(
            "Was ist Pflegegrad 3?",
            top_k=0,
        )

    vectorstore_service.similarity_search.assert_not_called()


def test_default_vectorstore_can_be_injected() -> None:
    service = RetrieverService(
        vectorstore_service=Mock(),
    )

    assert service.vectorstore_service is not None
