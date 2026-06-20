from __future__ import annotations

from unittest.mock import Mock

from app.domain.models import DocumentChunk, DocumentMetadata, StoredDocument
from app.services.document_processing_service import DocumentProcessingService


def _make_document() -> StoredDocument:
    metadata = DocumentMetadata(
        source="gesetze-im-internet",
        document_type="law",
        topic="krankenversicherung",
    )

    return StoredDocument(
        document_id="doc-1",
        source_path="data/raw/gesetze_im_internet/SGB_5.pdf",
        text="Raw   text\n\nwith   whitespace.",
        metadata=metadata,
    )


def test_process_cleans_text_and_chunks_document() -> None:
    document = _make_document()

    cleaning_service = Mock()
    cleaning_service.clean.return_value = "Cleaned text"

    chunk_1 = Mock(spec=DocumentChunk)
    chunk_2 = Mock(spec=DocumentChunk)

    chunking_service = Mock()
    chunking_service.split.return_value = [chunk_1, chunk_2]

    service = DocumentProcessingService(
        cleaning_service=cleaning_service,
        chunking_service=chunking_service,
    )

    result = service.process(document)

    assert result == [chunk_1, chunk_2]
    cleaning_service.clean.assert_called_once_with(document.text)
    chunking_service.split.assert_called_once_with(
        document=document,
        text="Cleaned text",
    )


def test_process_returns_empty_list_for_empty_cleaned_text() -> None:
    document = _make_document()

    cleaning_service = Mock()
    cleaning_service.clean.return_value = ""

    chunking_service = Mock()
    chunking_service.split.return_value = []

    service = DocumentProcessingService(
        cleaning_service=cleaning_service,
        chunking_service=chunking_service,
    )

    result = service.process(document)

    assert result == []
    cleaning_service.clean.assert_called_once_with(document.text)
    chunking_service.split.assert_called_once_with(
        document=document,
        text="",
    )


def test_process_uses_default_services() -> None:
    service = DocumentProcessingService()

    assert service.cleaning_service is not None
    assert service.chunking_service is not None
