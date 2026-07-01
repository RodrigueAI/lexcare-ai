from __future__ import annotations

from datetime import UTC, datetime, timedelta

from app.domain.models import DocumentMetadata, StoredDocument
from app.domain.warehouse import HubDocument, SatelliteDocumentContent, WarehouseKeyFactory
from app.services.satellite_document_content_service import (
    SatelliteDocumentContentService,
)


class FakeDocumentRepository:
    def __init__(self, documents: list[StoredDocument]) -> None:
        self._documents = list(documents)

    def list_documents(self) -> list[StoredDocument]:
        return list(self._documents)


class FakeHubDocumentRepository:
    def __init__(self, documents: list[HubDocument]) -> None:
        self.documents = list(documents)

    def get(self, document_key: str) -> HubDocument | None:
        for document in self.documents:
            if document.document_key == document_key:
                return document
        return None


class FakeContentRepository:
    def __init__(self) -> None:
        self.items: list[SatelliteDocumentContent] = []

    def load_all(self) -> list[SatelliteDocumentContent]:
        return list(self.items)

    def get(self, satellite_key: str) -> SatelliteDocumentContent | None:
        for item in self.items:
            if item.satellite_key == satellite_key:
                return item
        return None

    def find_versions(self, document_key: str) -> list[SatelliteDocumentContent]:
        return sorted(
            [item for item in self.items if item.document_key == document_key],
            key=lambda item: item.effective_from,
        )

    def find_latest(self, document_key: str) -> SatelliteDocumentContent | None:
        versions = self.find_versions(document_key)
        return versions[-1] if versions else None

    def find_as_of(
        self,
        document_key: str,
        moment: datetime,
    ) -> SatelliteDocumentContent | None:
        for item in reversed(self.find_versions(document_key)):
            if item.effective_from <= moment and (
                item.effective_to is None or moment < item.effective_to
            ):
                return item
        return None

    def save(self, satellite: SatelliteDocumentContent) -> None:
        self.items.append(satellite)

    def update(self, satellite: SatelliteDocumentContent) -> None:
        for index, current in enumerate(self.items):
            if current.satellite_key == satellite.satellite_key:
                self.items[index] = satellite
                return
        self.items.append(satellite)


def _make_stored_document(
    source_path: str,
    text: str,
) -> StoredDocument:
    metadata = DocumentMetadata(
        source="gesetze-im-internet",
        document_type="law",
        topic="healthcare-law",
        created_at=datetime(2024, 1, 1, tzinfo=UTC),
        extra={"topics": ["healthcare-law"]},
    )

    return StoredDocument(
        document_id="stored-1",
        source_path=source_path,
        text=text,
        metadata=metadata,
    )


def _make_hub_document(source_path: str) -> HubDocument:
    document_id = WarehouseKeyFactory.build_document_id(
        "gesetze-im-internet",
        source_path,
    )

    return HubDocument(
        document_key=WarehouseKeyFactory.create_document_key(document_id),
        document_id=document_id,
        source_key=WarehouseKeyFactory.create_source_key("gesetze-im-internet"),
        source_id="gesetze-im-internet",
        document_name="sample.pdf",
        source_path=source_path,
        created_at=datetime(2024, 1, 1, tzinfo=UTC),
    )


def test_sync_content_creates_initial_snapshot() -> None:
    stored = _make_stored_document(
        source_path="data/raw/a.pdf",
        text="First content version",
    )

    service = SatelliteDocumentContentService(
        document_repository=FakeDocumentRepository([stored]),
        hub_document_repository=FakeHubDocumentRepository([_make_hub_document("data/raw/a.pdf")]),
        repository=FakeContentRepository(),
    )

    created = service.sync_content()

    assert len(created) == 1
    assert created[0].is_current is True
    assert created[0].payload["text"] == "First content version"


def test_sync_content_creates_new_snapshot_on_change() -> None:
    v1 = _make_stored_document(
        source_path="data/raw/a.pdf",
        text="First content version",
    )
    v2 = _make_stored_document(
        source_path="data/raw/a.pdf",
        text="Second content version",
    )

    repo = FakeContentRepository()
    service = SatelliteDocumentContentService(
        document_repository=FakeDocumentRepository([v1, v2]),
        hub_document_repository=FakeHubDocumentRepository([_make_hub_document("data/raw/a.pdf")]),
        repository=repo,
    )

    created = service.sync_content()

    assert len(created) == 2

    versions = repo.find_versions(created[0].document_key)
    assert len(versions) == 2
    assert versions[0].is_current is False
    assert versions[1].is_current is True
    assert versions[0].effective_to is not None
    assert versions[1].effective_to is None
    assert versions[0].hash_diff != versions[1].hash_diff


def test_sync_content_skips_unchanged_snapshot() -> None:
    v1 = _make_stored_document(
        source_path="data/raw/a.pdf",
        text="Same content",
    )
    v2 = _make_stored_document(
        source_path="data/raw/a.pdf",
        text="Same content",
    )

    repo = FakeContentRepository()
    service = SatelliteDocumentContentService(
        document_repository=FakeDocumentRepository([v1, v2]),
        hub_document_repository=FakeHubDocumentRepository([_make_hub_document("data/raw/a.pdf")]),
        repository=repo,
    )

    created = service.sync_content()

    assert len(created) == 1
    assert len(repo.find_versions(created[0].document_key)) == 1


def test_get_as_of_returns_matching_snapshot() -> None:
    v1 = _make_stored_document(
        source_path="data/raw/a.pdf",
        text="First content version",
    )
    v2 = _make_stored_document(
        source_path="data/raw/a.pdf",
        text="Second content version",
    )

    repo = FakeContentRepository()
    service = SatelliteDocumentContentService(
        document_repository=FakeDocumentRepository([v1, v2]),
        hub_document_repository=FakeHubDocumentRepository([_make_hub_document("data/raw/a.pdf")]),
        repository=repo,
    )

    created = service.sync_content()
    moment = created[-1].effective_from + timedelta(microseconds=1)

    as_of = service.get_as_of(created[0].document_key, moment)

    assert as_of is not None
    assert as_of.hash_diff == created[-1].hash_diff
