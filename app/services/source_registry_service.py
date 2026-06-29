# app/services/source_registry_service.py
from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path
from typing import Any

import yaml

from app.domain.source import SourceDefinition
from app.repositories.source_registry import SourceRegistry


class SourceRegistryService:
    def __init__(self, registry_path: str = "data/source_registry.yaml") -> None:
        self.registry_path = Path(registry_path)
        self.registry = SourceRegistry(registry_path)

    def list_sources(self) -> list[SourceDefinition]:
        return self.registry.list_sources()

    def get(self, source_id: str) -> SourceDefinition | None:
        return self.registry.get(source_id)

    def register_source(
        self,
        *,
        source_id: str,
        name: str,
        source_type: str,
        description: str | None = None,
        enabled: bool = True,
        metadata: dict[str, Any] | None = None,
    ) -> SourceDefinition:
        source = SourceDefinition(
            source_id=source_id,
            name=name,
            source_type=source_type,
            description=description,
            enabled=enabled,
            metadata=metadata or {},
        )
        return self.upsert_source(source)

    def upsert_source(self, source: SourceDefinition) -> SourceDefinition:
        normalized = self._normalize_source(source)
        sources = self.list_sources()

        replaced = False
        for index, existing in enumerate(sources):
            if existing.source_id == normalized.source_id:
                sources[index] = normalized
                replaced = True
                break

        if not replaced:
            sources.append(normalized)

        self._write_sources(sources)
        return normalized

    def register_sources(
        self,
        sources: Iterable[SourceDefinition],
    ) -> list[SourceDefinition]:
        persisted: list[SourceDefinition] = []
        for source in sources:
            persisted.append(self.upsert_source(source))
        return persisted

    def _normalize_source(self, source: SourceDefinition) -> SourceDefinition:
        metadata = dict(source.metadata or {})
        topics = self._extract_topics(metadata)

        if topics:
            metadata["topics"] = topics
            metadata["topic"] = topics[0]
        else:
            existing_topic = metadata.get("topic")
            if isinstance(existing_topic, str) and existing_topic.strip():
                normalized_topic = existing_topic.strip()
                metadata["topic"] = normalized_topic
                metadata["topics"] = [normalized_topic]
            else:
                metadata["topics"] = []

        return SourceDefinition(
            source_id=source.source_id,
            name=source.name,
            source_type=source.source_type,
            description=source.description,
            enabled=source.enabled,
            metadata=metadata,
        )

    def _extract_topics(self, metadata: dict[str, Any]) -> list[str]:
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
        for topic in topics:
            key = topic.strip().lower()
            if key in seen:
                continue
            seen.add(key)
            result.append(topic.strip())

        return result

    def _write_sources(self, sources: list[SourceDefinition]) -> None:
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)

        payload = {"sources": [self._source_to_dict(source) for source in sources]}

        self.registry_path.write_text(
            yaml.safe_dump(
                payload,
                sort_keys=False,
                allow_unicode=True,
            ),
            encoding="utf-8",
        )

    def _source_to_dict(self, source: SourceDefinition) -> dict[str, Any]:
        return {
            "source_id": source.source_id,
            "name": source.name,
            "source_type": source.source_type,
            "description": source.description,
            "enabled": source.enabled,
            "metadata": source.metadata,
        }
