from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import Mock

from app.domain.ingestion import IngestionRecord
from app.domain.models import LoadedDocument, StoredDocument
from app.domain.source import SourceDefinition
from app.domain.source_artifact import SourceArtifact
from app.repositories.source_registry import SourceRegistry
from app.services.incremental_ingestion_service import IncrementalIngestionService


class FakeIngestionIndexRepository:
    def __init__(self) -> None:
        self.records: list[IngestionRecord] = []

    def find_latest(self, source_id: str, artifact_uri: str) -> IngestionRecord | None:
        matches = [
            record
            for record in self.records
            if record.source_id == source_id and record.artifact_uri == artifact_uri
        ]
        return matches[-1] if matches else None

    def save_record(self, record: IngestionRecord) -> None:
        self.records.append(record)


class FakeDocumentRepository:
    def __init__(self) -> None:
        self.saved: list[LoadedDocument] = []

    def save(self, document: LoadedDocument) -> StoredDocument:
        self.saved.append(document)
        return StoredDocument(
            document_id=f"doc-{len(self.saved)}",
            source_path=document.source_path,
            text=document.text,
            metadata=document.metadata,
        )


class FakeConnector:
    def __init__(self, artifacts: list[SourceArtifact]) -> None:
        self._artifacts = artifacts

    def fetch(self) -> list[SourceArtifact]:
        return self._artifacts


def test_ingest_skips_unchanged_documents(monkeypatch) -> None:
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
