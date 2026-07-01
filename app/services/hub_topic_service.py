# app/services/hub_topic_service.py
from __future__ import annotations

from datetime import UTC, datetime

from app.domain.warehouse import HubTopic, WarehouseKeyFactory
from app.repositories.contracts.source import SourceRegistryProtocol
from app.repositories.contracts.warehouse import HubTopicRepositoryProtocol
from app.repositories.hub_topic_repository import FileHubTopicRepository
from app.repositories.source_registry import SourceRegistry


class HubTopicService:
    def __init__(
        self,
        source_registry: SourceRegistryProtocol | None = None,
        repository: HubTopicRepositoryProtocol | None = None,
    ) -> None:
        self.source_registry = source_registry or SourceRegistry()
        self.repository = repository or FileHubTopicRepository()

    def sync_topics(self) -> list[HubTopic]:
        sources = self.source_registry.list_sources()
        created: list[HubTopic] = []

        for source in sources:
            for topic_name in self._extract_topics(source.metadata):
                topic_id = WarehouseKeyFactory.build_topic_id(topic_name)

                if self.repository.get(topic_id) is not None:
                    continue

                hub_topic = HubTopic(
                    topic_key=WarehouseKeyFactory.create_topic_key(topic_id),
                    topic_id=topic_id,
                    topic_name=topic_name,
                    created_at=datetime.now(UTC),
                )

                self.repository.save(hub_topic)
                created.append(hub_topic)

        return created

    def get(self, topic_id: str) -> HubTopic | None:
        return self.repository.get(topic_id)

    def _extract_topics(self, metadata: dict[str, object]) -> list[str]:
        topics: list[str] = []

        topic_value = metadata.get("topic")
        if isinstance(topic_value, str) and topic_value.strip():
            topics.append(topic_value.strip())

        topic_list = metadata.get("topics")
        if isinstance(topic_list, list):
            for item in topic_list:
                if isinstance(item, str) and item.strip():
                    topics.append(item.strip())

        seen: set[str] = set()
        result: list[str] = []
        for item in topics:
            normalized = item.strip()
            key = normalized.lower()
            if key in seen:
                continue
            seen.add(key)
            result.append(normalized)

        return result
