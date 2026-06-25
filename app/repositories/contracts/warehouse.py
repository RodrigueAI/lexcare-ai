# app/repositories/contracts/warehouse.py
from __future__ import annotations

from typing import Protocol

from app.domain.warehouse import HubDocument, HubSource, HubTopic


class HubSourceLookupRepositoryProtocol(Protocol):
    def get(self, source_id: str) -> HubSource | None: ...


class HubSourceRepositoryProtocol(HubSourceLookupRepositoryProtocol, Protocol):
    def save(self, hub_source: HubSource) -> None: ...


class HubDocumentRepositoryProtocol(Protocol):
    def get(self, document_key: str) -> HubDocument | None: ...

    def save(self, hub_document: HubDocument) -> None: ...


class HubTopicRepositoryProtocol(Protocol):
    def get(self, topic_id: str) -> HubTopic | None: ...

    def save(self, hub_topic: HubTopic) -> None: ...
