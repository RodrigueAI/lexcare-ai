# app/repositories/contracts/warehouse.py
from __future__ import annotations

from datetime import datetime
from typing import Protocol

from app.domain.warehouse import (
    HubDocument,
    HubSource,
    HubTopic,
    LinkDocumentTopic,
    SatelliteDocumentMetadata,
)


class HubSourceLookupRepositoryProtocol(Protocol):
    def get(self, source_id: str) -> HubSource | None: ...


class HubSourceRepositoryProtocol(HubSourceLookupRepositoryProtocol, Protocol):
    def save(self, hub_source: HubSource) -> None: ...


class HubDocumentLookupRepositoryProtocol(Protocol):
    def get(self, document_key: str) -> HubDocument | None: ...


class HubDocumentRepositoryProtocol(HubDocumentLookupRepositoryProtocol, Protocol):
    def save(self, hub_document: HubDocument) -> None: ...


class HubTopicLookupRepositoryProtocol(Protocol):
    def get(self, topic_id: str) -> HubTopic | None: ...


class HubTopicRepositoryProtocol(HubTopicLookupRepositoryProtocol, Protocol):
    def save(self, hub_topic: HubTopic) -> None: ...


class LinkDocumentTopicRepositoryProtocol(Protocol):
    def load_all(self) -> list[LinkDocumentTopic]: ...

    def get(self, link_key: str) -> LinkDocumentTopic | None: ...

    def save(self, link: LinkDocumentTopic) -> None: ...

    def find_by_document_key(self, document_key: str) -> list[LinkDocumentTopic]: ...

    def find_by_topic_key(self, topic_key: str) -> list[LinkDocumentTopic]: ...
class SatelliteDocumentMetadataRepositoryProtocol(Protocol):

    def load_all(self) -> list[SatelliteDocumentMetadata]: ...

    def get(self, satellite_key: str) -> SatelliteDocumentMetadata | None: ...

    def find_versions(self, document_key: str) -> list[SatelliteDocumentMetadata]: ...

    def find_latest(self, document_key: str) -> SatelliteDocumentMetadata | None: ...

    def find_as_of(
        self,
        document_key: str,
        moment: datetime,
    ) -> SatelliteDocumentMetadata | None: ...

    def save(self, satellite: SatelliteDocumentMetadata) -> None: ...

    def update(self, satellite: SatelliteDocumentMetadata) -> None: ...
