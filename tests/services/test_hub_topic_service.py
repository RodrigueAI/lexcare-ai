# app/services/test_hub_topic_service.py
from __future__ import annotations

from app.domain.source import SourceDefinition
from app.domain.warehouse import HubTopic
from app.services.hub_topic_service import HubTopicService


class FakeHubTopicRepository:
    def __init__(self) -> None:
        self.topics: list[HubTopic] = []

    def get(self, topic_id: str) -> HubTopic | None:
        for topic in self.topics:
            if topic.topic_id == topic_id:
                return topic
        return None

    def save(self, hub_topic: HubTopic) -> None:
        self.topics.append(hub_topic)


class FakeSourceRegistry:
    def __init__(self, sources: list[SourceDefinition]) -> None:
        self._sources = sources

    def list_sources(self) -> list[SourceDefinition]:
        return list(self._sources)

    def get(self, source_id: str) -> SourceDefinition | None:
        for source in self._sources:
            if source.source_id == source_id:
                return source
        return None


def test_sync_topics_creates_new_hub_entries() -> None:
    registry = FakeSourceRegistry(
        [
            SourceDefinition(
                source_id="gesetze-im-internet",
                name="Gesetze im Internet",
                source_type="file",
                metadata={"topic": "krankenversicherung"},
            ),
            SourceDefinition(
                source_id="pueg",
                name="PUEG",
                source_type="file",
                metadata={"topic": "pflegereform"},
            ),
        ]
    )

    repo = FakeHubTopicRepository()
    service = HubTopicService(source_registry=registry, repository=repo)

    created = service.sync_topics()

    assert len(created) == 2
    assert repo.get(created[0].topic_id) is not None


def test_sync_topics_skips_existing_entries() -> None:
    registry = FakeSourceRegistry(
        [
            SourceDefinition(
                source_id="gesetze-im-internet",
                name="Gesetze im Internet",
                source_type="file",
                metadata={"topic": "krankenversicherung"},
            )
        ]
    )

    repo = FakeHubTopicRepository()
    service = HubTopicService(source_registry=registry, repository=repo)

    first = service.sync_topics()
    second = service.sync_topics()

    assert len(first) == 1
    assert len(second) == 0
    assert len(repo.topics) == 1


def test_get_returns_topic_by_id() -> None:
    registry = FakeSourceRegistry(
        [
            SourceDefinition(
                source_id="gesetze-im-internet",
                name="Gesetze im Internet",
                source_type="file",
                metadata={"topic": "krankenversicherung"},
            )
        ]
    )

    repo = FakeHubTopicRepository()
    service = HubTopicService(source_registry=registry, repository=repo)

    created = service.sync_topics()
    found = service.get(created[0].topic_id)

    assert found is not None
    assert found.topic_id == created[0].topic_id
    assert found.topic_name == "krankenversicherung"
