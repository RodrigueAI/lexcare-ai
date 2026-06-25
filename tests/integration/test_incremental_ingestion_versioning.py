from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import Mock

from app.domain.models import LoadedDocument, StoredDocument
from app.domain.source import SourceDefinition
from app.domain.source_artifact import SourceArtifact
from app.repositories.contracts.document import DocumentWriteRepositoryProtocol
from app.repositories.document_version_repository import FileDocumentVersionRepository
from app.repositories.ingestion_index_repository import FileIngestionIndexRepository
from app.repositories.source_registry import SourceRegistry
from app.services.document_versioning_service import DocumentVersioningService
from app.services.incremental_ingestion_service import IncrementalIngestionService


class FakeConnector:
    def __init__(self, artifacts):
        self.artifacts = artifacts

    def fetch(self):
        return self.artifacts


class FakeDocumentRepository(DocumentWriteRepositoryProtocol):
    def __init__(self) -> None:
        self.counter = 0

    def save(self, document: LoadedDocument) -> StoredDocument:
        self.counter += 1
        return Mock(
            document_id=f"doc-{self.counter}",
            source_path=document.source_path,
            text=document.text,
            metadata=document.metadata,
        )


def test_incremental_ingestion_creates_versions(monkeypatch, tmp_path):
    source = SourceDefinition(
        source_id="test-source",
        name="Test Source",
        source_type="file",
        metadata={},
    )

    registry = Mock(spec=SourceRegistry)
    registry.get.return_value = source

    version_repo = FileDocumentVersionRepository(
        storage_path=str(tmp_path / "versions.json"),
    )
    index_repo = FileIngestionIndexRepository(
        storage_path=str(tmp_path / "ingestion_index.json"),
    )

    version_service = DocumentVersioningService(
        version_repository=version_repo,
    )

    artifact = SourceArtifact(
        source_id="test-source",
        source_type="file",
        title="doc",
        uri="file:///doc.txt",
        content="version-1",
        retrieved_at=datetime(2024, 1, 1, tzinfo=UTC),
        metadata={
            "document_type": "law",
            "topic": "test",
        },
    )

    monkeypatch.setattr(
        "app.services.incremental_ingestion_service.ConnectorFactory.create",
        lambda _source: FakeConnector([artifact]),
    )

    service = IncrementalIngestionService(
        source_registry=registry,
        document_repository=FakeDocumentRepository(),
        document_versioning_service=version_service,
        ingestion_index_repository=index_repo,
    )

    summary = service.ingest_source("test-source")

    assert summary.ingested == 1
    assert summary.skipped == 0
    assert summary.updated == 0
    assert summary.errors == 0

    versions = version_service.list_versions(
        "test-source",
        "file:///doc.txt",
    )

    assert len(versions) == 1
    assert versions[0].version_number == 1
