# app/services/incremental_ingestion_service.py
from __future__ import annotations

import hashlib
from datetime import UTC, datetime

from app.domain.ingestion import IngestionRecord, IngestionSummary
from app.domain.models import DocumentMetadata, LoadedDocument
from app.infrastructure.connectors import ConnectorFactory
from app.repositories.contracts.document import DocumentWriteRepositoryProtocol
from app.repositories.contracts.ingestion import IngestionIndexRepositoryProtocol
from app.repositories.contracts.source import SourceRegistryProtocol
from app.repositories.ingestion_index_repository import FileIngestionIndexRepository
from app.repositories.source_registry import SourceRegistry
from app.services.document_versioning_service import DocumentVersioningService


class IncrementalIngestionService:
    def __init__(
        self,
        source_registry: SourceRegistryProtocol | None = None,
        document_repository: DocumentWriteRepositoryProtocol | None = None,
        document_versioning_service: DocumentVersioningService | None = None,
        ingestion_index_repository: IngestionIndexRepositoryProtocol | None = None,
    ) -> None:
        self.source_registry = source_registry or SourceRegistry()

        if document_repository is None:
            raise ValueError("Document repository is required.")

        self.document_repository = document_repository
        self.document_versioning_service = (
            document_versioning_service or DocumentVersioningService()
        )
        self.ingestion_index_repository = (
            ingestion_index_repository or FileIngestionIndexRepository()
        )

    def ingest_source(self, source_id: str) -> IngestionSummary:
        source = self.source_registry.get(source_id)
        if source is None:
            raise ValueError(f"Unknown source: {source_id}")

        connector = ConnectorFactory.create(source)
        artifacts = connector.fetch()

        ingested = 0
        skipped = 0
        updated = 0
        errors = 0

        for artifact in artifacts:
            try:
                content_hash = self._hash_content(artifact.content)
                latest = self.ingestion_index_repository.find_latest(
                    source_id=artifact.source_id,
                    artifact_uri=artifact.uri,
                )

                if latest and latest.content_hash == content_hash:
                    skipped += 1
                    continue

                source_metadata = getattr(source, "metadata", {}) or {}

                document_type = self._first_non_empty(
                    artifact.metadata.get("document_type"),
                    source_metadata.get("document_type"),
                    default="unknown",
                )

                topic = self._first_non_empty(
                    artifact.metadata.get("topic"),
                    source_metadata.get("topic"),
                    default="unknown",
                )

                loaded_document = LoadedDocument(
                    source_path=artifact.uri,
                    text=artifact.content,
                    metadata=DocumentMetadata(
                        source=artifact.source_id,
                        document_type=document_type,
                        topic=topic,
                        created_at=artifact.retrieved_at,
                        extra={
                            **source_metadata,
                            **artifact.metadata,
                            "content_hash": content_hash,
                            "artifact_uri": artifact.uri,
                        },
                    ),
                )

                stored_document = self.document_repository.save(loaded_document)

                self.document_versioning_service.record_version(
                    source_id=artifact.source_id,
                    artifact_uri=artifact.uri,
                    stored_document=stored_document,
                    content_hash=content_hash,
                    effective_from=artifact.retrieved_at,
                    metadata=artifact.metadata,
                )

                record = IngestionRecord(
                    source_id=artifact.source_id,
                    artifact_uri=artifact.uri,
                    content_hash=content_hash,
                    document_id=stored_document.document_id,
                    ingested_at=datetime.now(UTC),
                    metadata=artifact.metadata,
                )
                self.ingestion_index_repository.save_record(record)

                if latest is None:
                    ingested += 1
                else:
                    updated += 1
            except Exception:
                errors += 1

        return IngestionSummary(
            source_id=source_id,
            fetched=len(artifacts),
            ingested=ingested,
            skipped=skipped,
            updated=updated,
            errors=errors,
        )

    def _hash_content(self, content: str) -> str:
        normalized = content.strip().encode("utf-8")
        return hashlib.sha256(normalized).hexdigest()

    def _first_non_empty(self, *values: object, default: str = "unknown") -> str:
        for value in values:
            if isinstance(value, str) and value.strip():
                return value.strip()
        return default
