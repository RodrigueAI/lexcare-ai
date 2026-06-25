# app/services/document_versioning_service.py
from __future__ import annotations

from dataclasses import replace
from datetime import UTC, datetime

from app.domain.models import StoredDocument
from app.domain.versioning import DocumentVersion
from app.repositories.contracts.versioning import DocumentVersionRepositoryProtocol
from app.repositories.document_version_repository import FileDocumentVersionRepository


class DocumentVersioningService:
    def __init__(
        self,
        version_repository: DocumentVersionRepositoryProtocol | None = None,
    ) -> None:
        self.version_repository = version_repository or FileDocumentVersionRepository()

    def record_version(
        self,
        *,
        source_id: str,
        artifact_uri: str,
        stored_document: StoredDocument,
        content_hash: str,
        effective_from: datetime | None = None,
        metadata: dict[str, object] | None = None,
    ) -> DocumentVersion:
        now = effective_from or datetime.now(UTC)
        latest = self.version_repository.find_latest(source_id, artifact_uri)

        if latest is not None and latest.content_hash == content_hash:
            return latest

        if latest is not None:
            closed_latest = replace(
                latest,
                effective_to=now,
                is_current=False,
            )
            self.version_repository.update_version(closed_latest)
            version_number = latest.version_number + 1
        else:
            version_number = 1

        version = DocumentVersion(
            document_id=stored_document.document_id,
            source_id=source_id,
            artifact_uri=artifact_uri,
            version_number=version_number,
            content_hash=content_hash,
            effective_from=now,
            effective_to=None,
            is_current=True,
            metadata=metadata or {},
        )

        self.version_repository.save_version(version)
        return version

    def get_current_version(
        self,
        source_id: str,
        artifact_uri: str,
    ) -> DocumentVersion | None:
        latest = self.version_repository.find_latest(source_id, artifact_uri)
        if latest is None:
            return None
        return latest if latest.is_current else None

    def list_versions(
        self,
        source_id: str,
        artifact_uri: str,
    ) -> list[DocumentVersion]:
        return self.version_repository.find_versions(source_id, artifact_uri)
