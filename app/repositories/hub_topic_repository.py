# app/repositories/hub_topic_repository.py
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from app.domain.warehouse import HubTopic


class FileHubTopicRepository:
    def __init__(self, storage_path: str = "data/warehouse/hub_topic.json") -> None:
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)

    def load_all(self) -> list[HubTopic]:
        if not self.storage_path.exists():
            return []

        data = json.loads(self.storage_path.read_text(encoding="utf-8"))
        return [
            HubTopic(
                topic_key=item["topic_key"],
                topic_id=item["topic_id"],
                topic_name=item["topic_name"],
                created_at=datetime.fromisoformat(item["created_at"]),
            )
            for item in data
        ]

    def get(self, topic_id: str) -> HubTopic | None:
        for topic in self.load_all():
            if topic.topic_id == topic_id:
                return topic
        return None

    def save(self, hub_topic: HubTopic) -> None:
        topics = self.load_all()

        if any(item.topic_id == hub_topic.topic_id for item in topics):
            return

        topics.append(hub_topic)
        self.storage_path.write_text(
            json.dumps(
                [
                    {
                        "topic_key": item.topic_key,
                        "topic_id": item.topic_id,
                        "topic_name": item.topic_name,
                        "created_at": item.created_at.isoformat(),
                    }
                    for item in topics
                ],
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
