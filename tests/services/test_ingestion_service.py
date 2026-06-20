from __future__ import annotations

from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from pydantic import SecretStr

from app.core.config import Settings
from app.domain.models import DocumentMetadata, LoadedDocument, StoredDocument
from app.services.ingestion_service import IngestionService


def _make_settings(tmp_path: Path) -> Settings:
    return Settings.model_construct(
        raw_upload_dir=str(tmp_path),
        azure_openai_endpoint="https://example.openai.azure.com/",
        azure_openai_api_version="2024-02-15-preview",
        azure_openai_deployment_name="gpt-4o-mini",
        azure_openai_api_key=SecretStr("fake-key"),
    )


def _make_loaded_document(source_path: str) -> LoadedDocument:
    return LoadedDocument(
        source_path=source_path,
        text="Extracted text",
        metadata=DocumentMetadata(
            source="gesetze-im-internet",
            document_type="law",
            topic="krankenversicherung",
            extra={
                "filename": "SGB_5.pdf",
                "page_count": 568,
                "file_size_bytes": 123456,
            },
        ),
    )


def _make_stored_document(source_path: str) -> StoredDocument:
    return StoredDocument(
        document_id="doc-1",
        source_path=source_path,
        text="Extracted text",
        metadata=_make_loaded_document(source_path).metadata,
    )


def test_ingest_pdf_bytes_happy_path(tmp_path: Path) -> None:
    settings = _make_settings(tmp_path)

    pdf_loader = Mock()
    repository = Mock()

    loaded_document = _make_loaded_document("data/raw/uploads/gesetze_im_internet/law/test.pdf")
    stored_document = _make_stored_document("data/raw/uploads/gesetze_im_internet/law/test.pdf")

    pdf_loader.load.return_value = loaded_document
    repository.save.return_value = stored_document

    service = IngestionService(
        pdf_loader=pdf_loader,
        repository=repository,
        settings=settings,
    )

    result = service.ingest_pdf_bytes(
        file_name="SGB_5.pdf",
        content=b"%PDF-1.4 fake content",
        source="gesetze-im-internet",
        document_type="law",
        topic="krankenversicherung",
    )

    assert result == stored_document

    pdf_loader.load.assert_called_once()
    repository.save.assert_called_once_with(loaded_document)


def test_ingest_pdf_bytes_rejects_non_pdf(tmp_path: Path) -> None:
    service = IngestionService(settings=_make_settings(tmp_path))

    with pytest.raises(ValueError, match="Only PDF files are supported"):
        service.ingest_pdf_bytes(
            file_name="notes.txt",
            content=b"hello",
            source="gesetze-im-internet",
            document_type="law",
            topic="krankenversicherung",
        )


def test_ingest_pdf_bytes_rejects_empty_content(tmp_path: Path) -> None:
    pdf_loader = Mock()
    repository = Mock()

    service = IngestionService(
        pdf_loader=pdf_loader,
        repository=repository,
        settings=_make_settings(tmp_path),
    )

    with pytest.raises(ValueError, match="Uploaded file is empty"):
        service.ingest_pdf_bytes(
            file_name="SGB_5.pdf",
            content=b"",
            source="gesetze-im-internet",
            document_type="law",
            topic="krankenversicherung",
        )

    pdf_loader.load.assert_not_called()
    repository.save.assert_not_called()


@patch("app.services.ingestion_service.uuid4", return_value="fixed-uuid")
def test_save_raw_pdf_writes_file_to_expected_location(
    mock_uuid4: Mock,
    tmp_path: Path,
) -> None:
    service = IngestionService(settings=_make_settings(tmp_path))

    target_path = service._save_raw_pdf(
        file_name="SGB_5.pdf",
        content=b"%PDF-1.4 fake content",
        source="gesetze-im-internet",
        document_type="law",
    )

    assert target_path.exists()
    assert target_path.read_bytes() == b"%PDF-1.4 fake content"
    assert target_path.name == "fixed-uuid_SGB_5.pdf"
    assert "gesetze_im_internet" in str(target_path)
    assert "law" in str(target_path)


def test_safe_segment_normalizes_values(tmp_path: Path) -> None:
    service = IngestionService(settings=_make_settings(tmp_path))

    assert service._safe_segment("Gesetze im Internet") == "gesetze_im_internet"
    assert service._safe_segment("  law  ") == "law"
    assert service._safe_segment("!!!") == "unknown"
