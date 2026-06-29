from pathlib import Path

import yaml

from app.domain.source import SourceDefinition


class SourceRegistry:
    def __init__(
        self,
        registry_path: str = "data/source_registry.yaml",
    ) -> None:
        self.registry_path = Path(registry_path)

    def list_sources(self) -> list[SourceDefinition]:
        if not self.registry_path.exists():
            return []

        data = yaml.safe_load(self.registry_path.read_text(encoding="utf-8")) or {}
        return [self._to_definition(item) for item in data.get("sources", [])]

    def get(
        self,
        source_id: str,
    ) -> SourceDefinition | None:
        for source in self.list_sources():
            if source.source_id == source_id:
                return source

        return None

    def _to_definition(
        self,
        item: dict,
    ) -> SourceDefinition:
        return SourceDefinition(
            source_id=item["source_id"],
            name=item["name"],
            source_type=item["source_type"],
            description=item.get("description"),
            enabled=item.get("enabled", True),
            metadata=item.get("metadata", {}),
        )
