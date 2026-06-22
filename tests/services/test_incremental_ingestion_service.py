from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import Mock

from app.domain.ingestion import IngestionRecord
from app.domain.models import LoadedDocument, StoredDocument
from app.domain.source import SourceDefinition
from app.domain.source_artifact import SourceArtifact
from app.repositories.contracts import (
    DocumentRepositoryProtocol,
    IngestionIndexRepositoryProtocol,
)
from app.repositories.source_registry import SourceRegistry
from app.services.incremental_ingestion_service import IncrementalIngestionService


class FakeIngestionIndexRepository(IngestionIndexRepositoryProtocol):
    def __init__(self) -> None:
        self.records: list[IngestionRecord] = []

    def load_all(self) -> list[IngestionRecord]:
        return list(self.records)

    def find_latest(self, source_id: str, artifact_uri: str) -> IngestionRecord | None:
        matches = [
            record
            for record in self.records
            if record.source_id == source_id and record.artifact_uri == artifact_uri
        ]
        return matches[-1] if matches else None

    def save_record(self, record: IngestionRecord) -> None:
        self.records.append(record)


class FakeDocumentRepository(DocumentRepositoryProtocol):
    def __init__(self) -> None:
        self.saved: list[StoredDocument] = []

    def save(self, document: LoadedDocument) -> StoredDocument:
        stored = StoredDocument(
            document_id=f"doc-{len(self.saved) + 1}",
            source_path=document.source_path,
            text=document.text,
            metadata=document.metadata,
        )
        self.saved.append(stored)
        return stored

    def read(self, document_id: str) -> StoredDocument:
        for document in self.saved:
            if document.document_id == document_id:
                return document
        raise FileNotFoundError(document_id)

    def list_documents(self) -> list[StoredDocument]:
        return list(self.saved)


class FakeConnector:
    def __init__(self, artifacts):
        self._artifacts = artifacts

    def fetch(self):
        return self._artifacts


def test_ingest_skips_unchanged_documents(monkeypatch):
    source = SourceDefinition(
        source_id="test",
        name="Test",
        source_type="file",
        metadata={},
    )

    registry = Mock(spec=SourceRegistry)
    registry.get.return_value = source

    artifact = SourceArtifact(
        source_id="test",
        source_type="file",
        title="doc",
        uri="file:///doc.pdf",
        content="same content",
        retrieved_at=datetime(2024, 1, 1, tzinfo=UTC),
        metadata={"document_type": "law", "topic": "health"},
    )

    doc_repo = FakeDocumentRepository()
    index_repo = FakeIngestionIndexRepository()

    service = IncrementalIngestionService(
        source_registry=registry,
        document_repository=doc_repo,
        ingestion_index_repository=index_repo,
    )

    monkeypatch.setattr(
        "app.services.incremental_ingestion_service.ConnectorFactory.create",
        lambda _source: FakeConnector([artifact]),
    )

    first = service.ingest_source("test")
    second = service.ingest_source("test")

    assert first.ingested == 1
    assert first.skipped == 0
    assert second.ingested == 0
    assert second.skipped == 1
    assert len(doc_repo.saved) == 1
