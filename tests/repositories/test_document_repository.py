from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pytest

from app.domain.models import DocumentMetadata, LoadedDocument
from app.repositories.document_repository import FileDocumentRepository


def _make_loaded_document() -> LoadedDocument:
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

    return LoadedDocument(
        source_path="data/raw/gesetze_im_internet/SGB_5.pdf",
        text="Sample text for repository tests.",
        metadata=metadata,
    )


def test_save_document_persists_json_file(tmp_path: Path) -> None:
    repo = FileDocumentRepository(storage_dir=str(tmp_path))
    document = _make_loaded_document()

    stored = repo.save(document)

    assert stored.document_id
    assert stored.source_path == document.source_path
    assert stored.text == document.text
    assert stored.metadata == document.metadata

    saved_file = tmp_path / f"{stored.document_id}.json"
    assert saved_file.exists()

    content = saved_file.read_text(encoding="utf-8")
    assert "Sample text for repository tests." in content
    assert "gesetze-im-internet" in content


def test_read_document_returns_same_data(tmp_path: Path) -> None:
    repo = FileDocumentRepository(storage_dir=str(tmp_path))
    document = _make_loaded_document()

    stored = repo.save(document)
    loaded = repo.read(stored.document_id)

    assert loaded.document_id == stored.document_id
    assert loaded.source_path == stored.source_path
    assert loaded.text == stored.text
    assert loaded.metadata == stored.metadata


def test_list_documents_returns_all_saved_documents(tmp_path: Path) -> None:
    repo = FileDocumentRepository(storage_dir=str(tmp_path))

    doc_1 = _make_loaded_document()
    doc_2 = _make_loaded_document()
    doc_2 = LoadedDocument(
        source_path="data/raw/gesetze_im_internet/SGB_11.pdf",
        text="Second sample text.",
        metadata=DocumentMetadata(
            source="gesetze-im-internet",
            document_type="law",
            topic="pflegeversicherung",
            created_at=datetime(2024, 1, 2, tzinfo=UTC),
            extra={
                "filename": "SGB_11.pdf",
                "page_count": 177,
                "file_size_bytes": 654321,
            },
        ),
    )

    stored_1 = repo.save(doc_1)
    stored_2 = repo.save(doc_2)

    documents = repo.list_documents()

    assert len(documents) == 2
    assert {doc.document_id for doc in documents} == {
        stored_1.document_id,
        stored_2.document_id,
    }


def test_read_missing_document_raises_file_not_found(tmp_path: Path) -> None:
    repo = FileDocumentRepository(storage_dir=str(tmp_path))

    with pytest.raises(FileNotFoundError, match="Document not found"):
        repo.read("does-not-exist")
