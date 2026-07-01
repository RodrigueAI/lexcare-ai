from __future__ import annotations

import hashlib
import json
from dataclasses import replace
from datetime import UTC, datetime
from typing import Any

from app.domain.models import StoredDocument
from app.domain.warehouse import WarehouseKeyFactory
from app.domain.warehouse.satellites import SatelliteDocumentContent
from app.repositories.contracts.document import DocumentListRepositoryProtocol
from app.repositories.contracts.warehouse import (
    HubDocumentLookupRepositoryProtocol,
    SatelliteDocumentContentRepositoryProtocol,
)
from app.repositories.satellite_document_content_repository import (
    FileSatelliteDocumentContentRepository,
)


class SatelliteDocumentContentService:
    def __init__(
        self,
        document_repository: DocumentListRepositoryProtocol,
        hub_document_repository: HubDocumentLookupRepositoryProtocol,
        repository: SatelliteDocumentContentRepositoryProtocol | None = None,
    ) -> None:
        self.document_repository = document_repository
        self.hub_document_repository = hub_document_repository
        self.repository = repository or FileSatelliteDocumentContentRepository()

    def sync_content(self) -> list[SatelliteDocumentContent]:
        created: list[SatelliteDocumentContent] = []

        for stored in self.document_repository.list_documents():
            document_key = self._build_document_key(
                source_id=stored.metadata.source,
                source_path=stored.source_path,
            )

            if self.hub_document_repository.get(document_key) is None:
                continue

            payload = self._build_payload(stored)
            hash_diff = self._build_hash_diff(payload)
            latest = self.repository.find_latest(document_key)

            if latest is not None and latest.hash_diff == hash_diff:
                continue

            now = datetime.now(UTC)

            if latest is not None:
                closed_latest = replace(
                    latest,
                    effective_to=now,
                    is_current=False,
                )
                self.repository.update(closed_latest)

            satellite = SatelliteDocumentContent(
                satellite_key=WarehouseKeyFactory.create_satellite_content_key(
                    document_key,
                    hash_diff,
                ),
                document_key=document_key,
                hash_diff=hash_diff,
                loaded_at=now,
                effective_from=now,
                effective_to=None,
                is_current=True,
                record_source="lexcare-ai",
                payload=payload,
            )

            self.repository.save(satellite)
            created.append(satellite)

        return created

    def get_current(self, document_key: str) -> SatelliteDocumentContent | None:
        return self.repository.find_latest(document_key)

    def list_versions(self, document_key: str) -> list[SatelliteDocumentContent]:
        return self.repository.find_versions(document_key)

    def get_as_of(
        self,
        document_key: str,
        moment: datetime,
    ) -> SatelliteDocumentContent | None:
        return self.repository.find_as_of(document_key, moment)

    def _build_payload(self, stored: StoredDocument) -> dict[str, Any]:
        return {
            "text": stored.text,
            "source_path": stored.source_path,
            "source": stored.metadata.source,
        }

    def _build_hash_diff(self, payload: dict[str, Any]) -> str:
        normalized = json.dumps(
            payload,
            sort_keys=True,
            ensure_ascii=False,
            default=str,
            separators=(",", ":"),
        )
        return hashlib.sha256(normalized.encode("utf-8")).hexdigest()

    def _build_document_key(self, source_id: str, source_path: str) -> str:
        document_id = WarehouseKeyFactory.build_document_id(source_id, source_path)
        return WarehouseKeyFactory.create_document_key(document_id)
