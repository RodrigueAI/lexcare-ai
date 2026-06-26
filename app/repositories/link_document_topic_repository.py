# app/repositories/link_document_topic_repository.py
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from app.domain.warehouse import LinkDocumentTopic


class FileLinkDocumentTopicRepository:
    def __init__(
        self,
        storage_path: str = "data/warehouse/link_document_topic.json",
    ) -> None:
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)

    def load_all(self) -> list[LinkDocumentTopic]:
        if not self.storage_path.exists():
            return []

        data = json.loads(self.storage_path.read_text(encoding="utf-8"))
        return [
            LinkDocumentTopic(
                link_key=item["link_key"],
                document_key=item["document_key"],
                topic_key=item["topic_key"],
                created_at=datetime.fromisoformat(item["created_at"]),
            )
            for item in data
        ]

    def get(self, link_key: str) -> LinkDocumentTopic | None:
        for link in self.load_all():
            if link.link_key == link_key:
                return link
        return None

    def save(self, link: LinkDocumentTopic) -> None:
        links = self.load_all()

        if any(item.link_key == link.link_key for item in links):
            return

        links.append(link)
        self.storage_path.write_text(
            json.dumps(
                [
                    {
                        "link_key": item.link_key,
                        "document_key": item.document_key,
                        "topic_key": item.topic_key,
                        "created_at": item.created_at.isoformat(),
                    }
                    for item in links
                ],
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

    def find_by_document_key(self, document_key: str) -> list[LinkDocumentTopic]:
        return [link for link in self.load_all() if link.document_key == document_key]

    def find_by_topic_key(self, topic_key: str) -> list[LinkDocumentTopic]:
        return [link for link in self.load_all() if link.topic_key == topic_key]
