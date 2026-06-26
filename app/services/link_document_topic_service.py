# app/services/link_document_topic_service.py
from __future__ import annotations

import hashlib
from datetime import UTC, datetime

from app.domain.models import StoredDocument
from app.domain.warehouse import LinkDocumentTopic
from app.repositories.contracts.document import DocumentListRepositoryProtocol
from app.repositories.contracts.warehouse import (
    HubDocumentLookupRepositoryProtocol,
    HubTopicLookupRepositoryProtocol,
    LinkDocumentTopicRepositoryProtocol,
)
from app.repositories.link_document_topic_repository import (
    FileLinkDocumentTopicRepository,
)


class LinkDocumentTopicService:
    def __init__(
        self,
        document_repository: DocumentListRepositoryProtocol,
        hub_document_repository: HubDocumentLookupRepositoryProtocol,
        hub_topic_repository: HubTopicLookupRepositoryProtocol,
        link_repository: LinkDocumentTopicRepositoryProtocol | None = None,
    ) -> None:
        self.document_repository = document_repository
        self.hub_document_repository = hub_document_repository
        self.hub_topic_repository = hub_topic_repository
        self.link_repository = link_repository or FileLinkDocumentTopicRepository()

    def sync_links(self) -> list[LinkDocumentTopic]:
        created: list[LinkDocumentTopic] = []

        for stored in self.document_repository.list_documents():
            document_key = self._build_document_key(
                source_id=stored.metadata.source,
                source_path=stored.source_path,
            )

            if self.hub_document_repository.get(document_key) is None:
                continue

            topic_names = self._extract_topic_names(stored)
            for topic_name in topic_names:
                topic_id = self._normalize_topic_id(topic_name)
                topic = self.hub_topic_repository.get(topic_id)
                if topic is None:
                    continue

                link_key = self._build_link_key(document_key, topic_id)
                if self.link_repository.get(link_key) is not None:
                    continue

                link = LinkDocumentTopic(
                    link_key=link_key,
                    document_key=document_key,
                    topic_key=topic_id,
                    created_at=datetime.now(UTC),
                )

                self.link_repository.save(link)
                created.append(link)

        return created

    def get(self, link_key: str) -> LinkDocumentTopic | None:
        return self.link_repository.get(link_key)

    def find_by_document_key(self, document_key: str) -> list[LinkDocumentTopic]:
        return self.link_repository.find_by_document_key(document_key)

    def find_by_topic_key(self, topic_key: str) -> list[LinkDocumentTopic]:
        return self.link_repository.find_by_topic_key(topic_key)

    def _extract_topic_names(self, stored: StoredDocument) -> list[str]:
        topics: list[str] = []

        primary_topic = stored.metadata.topic
        if isinstance(primary_topic, str) and primary_topic.strip():
            topics.append(primary_topic.strip())

        extra_topics = stored.metadata.extra.get("topics")
        if isinstance(extra_topics, list):
            for item in extra_topics:
                if isinstance(item, str) and item.strip():
                    topics.append(item.strip())

        seen: set[str] = set()
        result: list[str] = []
        for topic in topics:
            normalized = topic.strip()
            key = normalized.lower()
            if key in seen:
                continue
            seen.add(key)
            result.append(normalized)

        return result

    def _build_document_key(self, source_id: str, source_path: str) -> str:
        raw = f"{source_id}|{source_path}".encode()
        return hashlib.sha256(raw).hexdigest()

    def _normalize_topic_id(self, topic_name: str) -> str:
        raw = topic_name.strip().lower().encode("utf-8")
        return hashlib.sha256(raw).hexdigest()

    def _build_link_key(self, document_key: str, topic_key: str) -> str:
        raw = f"{document_key}|{topic_key}".encode()
        return hashlib.sha256(raw).hexdigest()
