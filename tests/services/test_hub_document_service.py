# tests/services/test_hub_document_service.py
from __future__ import annotations

from datetime import UTC, datetime

from app.domain.models import DocumentMetadata, StoredDocument
from app.domain.warehouse import HubDocument, HubSource
from app.services.hub_document_service import HubDocumentService


class FakeHubSourceRepository:
    def __init__(self) -> None:
        self.sources = [
            HubSource(
                source_key="source-key-1",
                source_id="gesetze-im-internet",
                source_name="Gesetze im Internet",
                created_at=datetime(2024, 1, 1, tzinfo=UTC),
            )
        ]

    def get(self, source_id: str):
        for source in self.sources:
            if source.source_id == source_id:
                return source
        return None


class FakeHubDocumentRepository:
    def __init__(self) -> None:
        self.documents: list[HubDocument] = []

    def load_all(self) -> list[HubDocument]:
        return list(self.documents)

    def get(self, document_key: str):
        for document in self.documents:
            if document.document_key == document_key:
                return document
        return None

    def save(self, hub_document: HubDocument) -> None:
        self.documents.append(hub_document)


class FakeDocumentRepository:
    def __init__(self, documents: list[StoredDocument]) -> None:
        self._documents = documents

    def list_documents(self) -> list[StoredDocument]:
        return list(self._documents)


def _make_stored_document(document_id: str, source_path: str, filename: str) -> StoredDocument:
    metadata = DocumentMetadata(
        source="gesetze-im-internet",
        document_type="law",
        topic="krankenversicherung",
        created_at=datetime(2024, 1, 1, tzinfo=UTC),
        extra={"filename": filename},
    )
    return StoredDocument(
        document_id=document_id,
        source_path=source_path,
        text="sample text",
        metadata=metadata,
    )


def test_sync_documents_creates_new_hub_entries() -> None:
    doc_repo = FakeDocumentRepository(
        [
            _make_stored_document("doc-1", "data/raw/a.pdf", "a.pdf"),
            _make_stored_document("doc-2", "data/raw/b.pdf", "b.pdf"),
        ]
    )

    service = HubDocumentService(
        document_repository=doc_repo,
        hub_source_repository=FakeHubSourceRepository(),
        hub_document_repository=FakeHubDocumentRepository(),
    )

    created = service.sync_documents()

    assert len(created) == 2
    assert created[0].source_id == "gesetze-im-internet"
    assert created[0].source_key == "source-key-1"


def test_sync_documents_skips_existing_entries() -> None:
    doc_repo = FakeDocumentRepository(
        [
            _make_stored_document("doc-1", "data/raw/a.pdf", "a.pdf"),
        ]
    )
    hub_doc_repo = FakeHubDocumentRepository()

    service = HubDocumentService(
        document_repository=doc_repo,
        hub_source_repository=FakeHubSourceRepository(),
        hub_document_repository=hub_doc_repo,
    )

    first = service.sync_documents()
    second = service.sync_documents()

    assert len(first) == 1
    assert len(second) == 0
    assert len(hub_doc_repo.documents) == 1


def test_get_returns_document_by_key() -> None:
    hub_doc_repo = FakeHubDocumentRepository()
    source_repo = FakeHubSourceRepository()
    doc_repo = FakeDocumentRepository(
        [
            _make_stored_document("doc-1", "data/raw/a.pdf", "a.pdf"),
        ]
    )

    service = HubDocumentService(
        document_repository=doc_repo,
        hub_source_repository=source_repo,
        hub_document_repository=hub_doc_repo,
    )

    created = service.sync_documents()
    found = service.get(created[0].document_key)

    assert found is not None
    assert found.document_key == created[0].document_key
