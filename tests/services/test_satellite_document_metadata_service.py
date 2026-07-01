# tests/services/test_satellite_document_metadata_service.py
from __future__ import annotations

from datetime import UTC, datetime, timedelta

from app.domain.models import DocumentMetadata, StoredDocument
from app.domain.warehouse import HubDocument, SatelliteDocumentMetadata, WarehouseKeyFactory
from app.services.satellite_document_metadata_service import (
    SatelliteDocumentMetadataService,
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


class FakeSatelliteRepository:
    def __init__(self) -> None:
        self.satellites: list[SatelliteDocumentMetadata] = []

    def load_all(self) -> list[SatelliteDocumentMetadata]:
        return list(self.satellites)

    def get(self, satellite_key: str) -> SatelliteDocumentMetadata | None:
        for satellite in self.satellites:
            if satellite.satellite_key == satellite_key:
                return satellite
        return None

    def find_versions(self, document_key: str) -> list[SatelliteDocumentMetadata]:
        return sorted(
            [satellite for satellite in self.satellites if satellite.document_key == document_key],
            key=lambda item: item.effective_from,
        )

    def find_latest(self, document_key: str) -> SatelliteDocumentMetadata | None:
        versions = self.find_versions(document_key)
        return versions[-1] if versions else None

    def find_as_of(
        self,
        document_key: str,
        moment: datetime,
    ) -> SatelliteDocumentMetadata | None:
        for satellite in reversed(self.find_versions(document_key)):
            if satellite.effective_from <= moment and (
                satellite.effective_to is None or moment < satellite.effective_to
            ):
                return satellite
        return None

    def save(self, satellite: SatelliteDocumentMetadata) -> None:
        self.satellites.append(satellite)

    def update(self, satellite: SatelliteDocumentMetadata) -> None:
        for index, current in enumerate(self.satellites):
            if current.satellite_key == satellite.satellite_key:
                self.satellites[index] = satellite
                return
        self.satellites.append(satellite)


def _make_stored_document(
    source_path: str,
    topic: str,
    topics: list[str] | None = None,
    document_type: str = "law",
) -> StoredDocument:
    metadata = DocumentMetadata(
        source="gesetze-im-internet",
        document_type=document_type,
        topic=topic,
        created_at=datetime(2024, 1, 1, tzinfo=UTC),
        extra={
            "filename": "sample.pdf",
            "topics": topics or [],
        },
    )

    return StoredDocument(
        document_id="stored-1",
        source_path=source_path,
        text="sample text",
        metadata=metadata,
    )


def _make_hub_document(source_path: str) -> HubDocument:
    document_id = WarehouseKeyFactory.build_document_id(
        "gesetze-im-internet",
        source_path,
    )
    document_key = WarehouseKeyFactory.create_document_key(document_id)

    return HubDocument(
        document_key=document_key,
        document_id=document_id,
        source_key=WarehouseKeyFactory.create_source_key("gesetze-im-internet"),
        source_id="gesetze-im-internet",
        document_name="sample.pdf",
        source_path=source_path,
        created_at=datetime(2024, 1, 1, tzinfo=UTC),
    )


def test_sync_metadata_creates_initial_snapshot() -> None:
    stored = _make_stored_document(
        source_path="data/raw/a.pdf",
        topic="healthcare-law",
        topics=["healthcare-policy"],
    )

    service = SatelliteDocumentMetadataService(
        document_repository=FakeDocumentRepository([stored]),
        hub_document_repository=FakeHubDocumentRepository([_make_hub_document("data/raw/a.pdf")]),
        repository=FakeSatelliteRepository(),
    )

    created = service.sync_metadata()

    assert len(created) == 1
    assert created[0].is_current is True
    assert created[0].payload["topic"] == "healthcare-law"
    assert created[0].payload["topics"] == ["healthcare-law", "healthcare-policy"]


def test_sync_metadata_creates_new_snapshot_on_change() -> None:
    v1 = _make_stored_document(
        source_path="data/raw/a.pdf",
        topic="healthcare-law",
        topics=["healthcare-policy"],
    )
    v2 = _make_stored_document(
        source_path="data/raw/a.pdf",
        topic="healthcare-policy",
        topics=["healthcare-policy", "legislation"],
        document_type="regulation",
    )

    repo = FakeSatelliteRepository()
    service = SatelliteDocumentMetadataService(
        document_repository=FakeDocumentRepository([v1, v2]),
        hub_document_repository=FakeHubDocumentRepository([_make_hub_document("data/raw/a.pdf")]),
        repository=repo,
    )

    created = service.sync_metadata()

    assert len(created) == 2

    versions = repo.find_versions(created[0].document_key)
    assert len(versions) == 2
    assert versions[0].is_current is False
    assert versions[1].is_current is True
    assert versions[0].effective_to is not None
    assert versions[1].effective_to is None
    assert versions[0].hash_diff != versions[1].hash_diff


def test_sync_metadata_skips_unchanged_snapshot() -> None:
    stored_1 = _make_stored_document(
        source_path="data/raw/a.pdf",
        topic="healthcare-law",
        topics=["healthcare-policy"],
    )
    stored_2 = _make_stored_document(
        source_path="data/raw/a.pdf",
        topic="healthcare-law",
        topics=["healthcare-policy"],
    )

    repo = FakeSatelliteRepository()
    service = SatelliteDocumentMetadataService(
        document_repository=FakeDocumentRepository([stored_1, stored_2]),
        hub_document_repository=FakeHubDocumentRepository([_make_hub_document("data/raw/a.pdf")]),
        repository=repo,
    )

    created = service.sync_metadata()

    assert len(created) == 1
    assert len(repo.find_versions(created[0].document_key)) == 1


def test_get_as_of_returns_matching_snapshot() -> None:
    stored_1 = _make_stored_document(
        source_path="data/raw/a.pdf",
        topic="healthcare-law",
    )
    stored_2 = _make_stored_document(
        source_path="data/raw/a.pdf",
        topic="healthcare-policy",
        document_type="regulation",
    )

    repo = FakeSatelliteRepository()
    service = SatelliteDocumentMetadataService(
        document_repository=FakeDocumentRepository([stored_1, stored_2]),
        hub_document_repository=FakeHubDocumentRepository([_make_hub_document("data/raw/a.pdf")]),
        repository=repo,
    )

    created = service.sync_metadata()
    moment = created[-1].effective_from + timedelta(microseconds=1)

    as_of = service.get_as_of(created[0].document_key, moment)

    assert as_of is not None
    assert as_of.hash_diff == created[-1].hash_diff
