from __future__ import annotations

from typing import Protocol

from app.domain.warehouse import HubDocument, HubSource


class HubSourceLookupRepositoryProtocol(Protocol):
    def get(self, source_id: str) -> HubSource | None: ...


class HubSourceRepositoryProtocol(HubSourceLookupRepositoryProtocol, Protocol):
    def save(self, hub_source: HubSource) -> None: ...


class HubDocumentRepositoryProtocol(Protocol):
    def get(self, document_key: str) -> HubDocument | None: ...
    def save(self, hub_document: HubDocument) -> None: ...
