# app/repositories/contracts/warehouse.py
from __future__ import annotations

from typing import Protocol

from app.domain.warehouse import (
    HubDocument,
    HubSource,
    HubTopic,
    LinkDocumentTopic,
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
