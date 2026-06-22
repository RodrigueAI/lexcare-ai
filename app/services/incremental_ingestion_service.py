from __future__ import annotations

import hashlib
from datetime import UTC, datetime

from app.domain.ingestion import IngestionRecord, IngestionSummary
from app.domain.models import DocumentMetadata, LoadedDocument
from app.infrastructure.connectors import ConnectorFactory
from app.repositories.document_repository import DocumentRepository
from app.repositories.ingestion_index_repository import FileIngestionIndexRepository
from app.repositories.source_registry import SourceRegistry


class IncrementalIngestionService:
    def __init__(
        self,
        source_registry: SourceRegistry | None = None,
        document_repository: DocumentRepository | None = None,
        ingestion_index_repository: FileIngestionIndexRepository | None = None,
    ) -> None:
        self.source_registry = source_registry or SourceRegistry()
        self.document_repository = document_repository
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

                loaded_document = LoadedDocument(
                    source_path=artifact.uri,
                    text=artifact.content,
                    metadata=DocumentMetadata(
                        source=artifact.source_id,
                        document_type=artifact.metadata.get("document_type", "unknown"),
                        topic=artifact.metadata.get("topic", "unknown"),
                        created_at=(
                            artifact.retrieved_at
                            if hasattr(artifact, "retrieved_at")
                            else datetime.now(UTC)
                        ),
                        extra={
                            **artifact.metadata,
                            "content_hash": content_hash,
                            "artifact_uri": artifact.uri,
                        },
                    ),
                )

                stored_document = self.document_repository.save(loaded_document)

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
