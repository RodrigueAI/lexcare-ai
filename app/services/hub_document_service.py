# app/services/hub_document_service.py
from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import unquote, urlparse

from app.domain.keys import WarehouseKeyFactory
from app.domain.warehouse import HubDocument
from app.repositories.contracts.document import DocumentListRepositoryProtocol
from app.repositories.contracts.warehouse import (
    HubDocumentRepositoryProtocol,
    HubSourceLookupRepositoryProtocol,
)


class HubDocumentService:
    def __init__(
        self,
        document_repository: DocumentListRepositoryProtocol | None = None,
        hub_source_repository: HubSourceLookupRepositoryProtocol | None = None,
        hub_document_repository: HubDocumentRepositoryProtocol | None = None,
    ) -> None:
        if document_repository is None:
            raise ValueError("Document repository is required.")
        if hub_source_repository is None:
            raise ValueError("Hub source repository is required.")
        if hub_document_repository is None:
            raise ValueError("Hub document repository is required.")

        self.document_repository: DocumentListRepositoryProtocol = document_repository
        self.hub_source_repository: HubSourceLookupRepositoryProtocol = hub_source_repository

        self.hub_document_repository: HubDocumentRepositoryProtocol = hub_document_repository

    def sync_documents(self) -> list[HubDocument]:
        stored_documents = self.document_repository.list_documents()
        created: list[HubDocument] = []

        for stored in stored_documents:
            source_id = stored.metadata.source
            source = self.hub_source_repository.get(source_id)
            if source is None:
                continue

            document_id = WarehouseKeyFactory.build_document_id(source_id, stored.source_path)
            document_key = WarehouseKeyFactory.create_document_key(document_id)

            if self.hub_document_repository.get(document_key) is not None:
                continue

            hub_document = HubDocument(
                document_key=document_key,
                document_id=document_id,
                source_key=source.source_key,
                source_id=source_id,
                document_name=self._extract_document_name(stored.source_path),
                source_path=stored.source_path,
                created_at=datetime.now(UTC),
            )

            self.hub_document_repository.save(hub_document)
            created.append(hub_document)

        return created

    def _extract_document_name(self, source_path: str) -> str:
        parsed = urlparse(source_path)
        if parsed.scheme == "file":
            return Path(unquote(parsed.path)).name
        return Path(source_path).name

    def get(self, document_key: str) -> HubDocument | None:
        return self.hub_document_repository.get(document_key)
