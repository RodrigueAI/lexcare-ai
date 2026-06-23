from __future__ import annotations

from datetime import UTC, datetime

from app.domain.models import DocumentMetadata, StoredDocument
from app.domain.versioning import DocumentVersion
from app.services.document_versioning_service import DocumentVersioningService


class FakeDocumentVersionRepository:
    def __init__(self) -> None:
        self.versions: list[DocumentVersion] = []

    def load_all(self) -> list[DocumentVersion]:
        return list(self.versions)

    def find_versions(self, source_id: str, artifact_uri: str) -> list[DocumentVersion]:
        return [
            version
            for version in self.versions
            if version.source_id == source_id and version.artifact_uri == artifact_uri
        ]

    def find_latest(self, source_id: str, artifact_uri: str) -> DocumentVersion | None:
        versions = self.find_versions(source_id, artifact_uri)
        if not versions:
            return None
        return sorted(versions, key=lambda item: item.version_number)[-1]

    def save_version(self, version: DocumentVersion) -> None:
        self.versions.append(version)

    def update_version(self, version: DocumentVersion) -> None:
        for index, item in enumerate(self.versions):
            if item.document_id == version.document_id:
                self.versions[index] = version
                return
        self.versions.append(version)


def _make_stored_document(document_id: str) -> StoredDocument:
    metadata = DocumentMetadata(
        source="gesetze-im-internet",
        document_type="law",
        topic="krankenversicherung",
        created_at=datetime(2024, 1, 1, tzinfo=UTC),
        extra={"filename": "SGB_5.pdf"},
    )

    return StoredDocument(
        document_id=document_id,
        source_path="data/raw/gesetze_im_internet/SGB_5.pdf",
        text="Sample content",
        metadata=metadata,
    )


def test_record_version_creates_first_version() -> None:
    repo = FakeDocumentVersionRepository()
    service = DocumentVersioningService(version_repository=repo)

    version = service.record_version(
        source_id="gesetze-im-internet",
        artifact_uri="file:///SGB_5.pdf",
        stored_document=_make_stored_document("doc-1"),
        content_hash="hash-1",
        effective_from=datetime(2024, 1, 1, tzinfo=UTC),
        metadata={"filename": "SGB_5.pdf"},
    )

    assert version.version_number == 1
    assert version.is_current is True
    assert version.effective_to is None
    assert len(repo.versions) == 1


def test_record_version_skips_when_content_unchanged() -> None:
    repo = FakeDocumentVersionRepository()
    service = DocumentVersioningService(version_repository=repo)

    first = service.record_version(
        source_id="gesetze-im-internet",
        artifact_uri="file:///SGB_5.pdf",
        stored_document=_make_stored_document("doc-1"),
        content_hash="hash-1",
        effective_from=datetime(2024, 1, 1, tzinfo=UTC),
        metadata={"filename": "SGB_5.pdf"},
    )

    second = service.record_version(
        source_id="gesetze-im-internet",
        artifact_uri="file:///SGB_5.pdf",
        stored_document=_make_stored_document("doc-2"),
        content_hash="hash-1",
        effective_from=datetime(2024, 1, 2, tzinfo=UTC),
        metadata={"filename": "SGB_5.pdf"},
    )

    assert second.document_id == first.document_id
    assert second.version_number == 1
    assert len(repo.versions) == 1


def test_record_version_closes_previous_version_when_content_changes() -> None:
    repo = FakeDocumentVersionRepository()
    service = DocumentVersioningService(version_repository=repo)

    first = service.record_version(
        source_id="gesetze-im-internet",
        artifact_uri="file:///SGB_5.pdf",
        stored_document=_make_stored_document("doc-1"),
        content_hash="hash-1",
        effective_from=datetime(2024, 1, 1, tzinfo=UTC),
        metadata={"filename": "SGB_5.pdf"},
    )

    second = service.record_version(
        source_id="gesetze-im-internet",
        artifact_uri="file:///SGB_5.pdf",
        stored_document=_make_stored_document("doc-2"),
        content_hash="hash-2",
        effective_from=datetime(2024, 1, 2, tzinfo=UTC),
        metadata={"filename": "SGB_5.pdf"},
    )

    assert first.version_number == 1
    assert second.version_number == 2
    assert len(repo.versions) == 2

    closed_first = repo.find_versions("gesetze-im-internet", "file:///SGB_5.pdf")[0]
    current_second = repo.find_versions("gesetze-im-internet", "file:///SGB_5.pdf")[1]

    assert closed_first.is_current is False
    assert closed_first.effective_to == datetime(2024, 1, 2, tzinfo=UTC)
    assert current_second.is_current is True
