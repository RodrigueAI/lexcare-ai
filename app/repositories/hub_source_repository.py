# app/repositories/hub_source_repository.py
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from app.domain.warehouse import HubSource


class FileHubSourceRepository:
    def __init__(
        self,
        storage_path: str = "data/warehouse/hub_source.json",
    ) -> None:
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

    def load_all(self) -> list[HubSource]:
        if not self.storage_path.exists():
            return []

        data = json.loads(
            self.storage_path.read_text(
                encoding="utf-8",
            )
        )

        return [
            HubSource(
                source_key=item["source_key"],
                source_id=item["source_id"],
                source_name=item["source_name"],
                created_at=datetime.fromisoformat(
                    item["created_at"],
                ),
            )
            for item in data
        ]

    def save(
        self,
        hub_source: HubSource,
    ) -> None:
        sources = self.load_all()

        if any(item.source_id == hub_source.source_id for item in sources):
            return

        sources.append(hub_source)

        payload = [
            {
                "source_key": item.source_key,
                "source_id": item.source_id,
                "source_name": item.source_name,
                "created_at": item.created_at.isoformat(),
            }
            for item in sources
        ]

        self.storage_path.write_text(
            json.dumps(
                payload,
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

    def get(
        self,
        source_id: str,
    ) -> HubSource | None:
        for source in self.load_all():
            if source.source_id == source_id:
                return source

        return None
