from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from app.domain.warehouse import HubSource
from app.repositories.contracts.source import SourceRegistryProtocol
from app.repositories.contracts.warehouse import HubSourceRepositoryProtocol
from app.repositories.hub_source_repository import FileHubSourceRepository
from app.repositories.source_registry import SourceRegistry


class HubSourceService:
    def __init__(
        self,
        source_registry: SourceRegistryProtocol | None = None,
        repository: HubSourceRepositoryProtocol | None = None,
    ) -> None:
        self.source_registry = source_registry or SourceRegistry()
        self.repository = repository or FileHubSourceRepository()

    def sync_sources(self) -> list[HubSource]:
        registry_sources = self.source_registry.list_sources()
        created: list[HubSource] = []

        for source in registry_sources:
            existing = self.repository.get(source.source_id)
            if existing is not None:
                continue

            hub_source = HubSource(
                source_key=str(uuid4()),
                source_id=source.source_id,
                source_name=source.name,
                created_at=datetime.now(UTC),
            )

            self.repository.save(hub_source)
            created.append(hub_source)

        return created
