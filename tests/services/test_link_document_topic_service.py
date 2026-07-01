from __future__ import annotations

from datetime import UTC, datetime

from app.domain.models import DocumentMetadata, StoredDocument
from app.domain.warehouse import HubDocument, HubTopic, LinkDocumentTopic
from app.domain.warehouse.keys import WarehouseKeyFactory
from app.services.link_document_topic_service import LinkDocumentTopicService


class FakeDocumentRepository:
    def __init__(self, documents: list[StoredDocument]) -> None:
        self._documents = list(documents)

    def list_documents(self) -> list[StoredDocument]:
        return list(self._documents)


class FakeHubDocumentRepository:
    def __init__(self, documents: list[HubDocument]) -> None:
        self.documents = list(documents)

    def get(self, document_key: str) -> HubDocument | None:
        for document in self.documents:
            if document.document_key == document_key:
                return document
        return None


class FakeHubTopicRepository:
    def __init__(self, topics: list[HubTopic]) -> None:
        self.topics = list(topics)

    def get(self, topic_id: str) -> HubTopic | None:
        for topic in self.topics:
            if topic.topic_id == topic_id:
                return topic
        return None


class FakeLinkRepository:
    def __init__(self) -> None:
        self.links: list[LinkDocumentTopic] = []

    def load_all(self) -> list[LinkDocumentTopic]:
        return list(self.links)

    def get(self, link_key: str) -> LinkDocumentTopic | None:
        for link in self.links:
            if link.link_key == link_key:
                return link
        return None

    def save(self, link: LinkDocumentTopic) -> None:
        self.links.append(link)

    def find_by_document_key(self, document_key: str) -> list[LinkDocumentTopic]:
        return [link for link in self.links if link.document_key == document_key]

    def find_by_topic_key(self, topic_key: str) -> list[LinkDocumentTopic]:
        return [link for link in self.links if link.topic_key == topic_key]


def _make_stored_document(
    document_id: str,
    source_path: str,
    topic: str,
    topics: list[str] | None = None,
) -> StoredDocument:
    metadata = DocumentMetadata(
        source="gesetze-im-internet",
        document_type="law",
        topic=topic,
        created_at=datetime(2024, 1, 1, tzinfo=UTC),
        extra={
            "filename": "sample.pdf",
            "topics": topics or [],
        },
    )

    return StoredDocument(
        document_id=document_id,
        source_path=source_path,
        text="sample text",
        metadata=metadata,
    )


def _make_hub_document(document_id: str, source_path: str) -> HubDocument:

    business_id = WarehouseKeyFactory.build_document_id(
        "gesetze-im-internet",
        source_path,
    )

    return HubDocument(
        document_key=WarehouseKeyFactory.create_document_key(business_id),
        document_id=business_id,
        source_key="source-key-1",
        source_id="gesetze-im-internet",
        document_name="sample.pdf",
        source_path=source_path,
        created_at=datetime(2024, 1, 1, tzinfo=UTC),
    )


def _make_topic(topic_name: str) -> HubTopic:
    topic_id = WarehouseKeyFactory.build_topic_id(topic_name)

    return HubTopic(
        topic_key=WarehouseKeyFactory.create_topic_key(topic_id),
        topic_id=topic_id,
        topic_name=topic_name,
        created_at=datetime(2024, 1, 1, tzinfo=UTC),
    )


def test_sync_links_creates_many_to_many_relationships() -> None:
    stored = _make_stored_document(
        document_id="doc-1",
        source_path="data/raw/a.pdf",
        topic="krankenversicherung",
        topics=["pflegeversicherung"],
    )

    service = LinkDocumentTopicService(
        document_repository=FakeDocumentRepository([stored]),
        hub_document_repository=FakeHubDocumentRepository(
            [_make_hub_document("doc-1", "data/raw/a.pdf")]
        ),
        hub_topic_repository=FakeHubTopicRepository(
            [_make_topic("krankenversicherung"), _make_topic("pflegeversicherung")]
        ),
        link_repository=FakeLinkRepository(),
    )

    created = service.sync_links()

    assert len(created) == 2
    assert len(service.find_by_document_key(created[0].document_key)) == 2


def test_sync_links_skips_existing_relationships() -> None:
    stored = _make_stored_document(
        document_id="doc-1",
        source_path="data/raw/a.pdf",
        topic="krankenversicherung",
    )

    link_repo = FakeLinkRepository()
    service = LinkDocumentTopicService(
        document_repository=FakeDocumentRepository([stored]),
        hub_document_repository=FakeHubDocumentRepository(
            [_make_hub_document("doc-1", "data/raw/a.pdf")]
        ),
        hub_topic_repository=FakeHubTopicRepository([_make_topic("krankenversicherung")]),
        link_repository=link_repo,
    )

    first = service.sync_links()
    second = service.sync_links()

    assert len(first) == 1
    assert len(second) == 0
    assert len(link_repo.links) == 1


def test_find_by_topic_key_returns_related_links() -> None:
    stored = _make_stored_document(
        document_id="doc-1",
        source_path="data/raw/a.pdf",
        topic="krankenversicherung",
    )

    link_repo = FakeLinkRepository()
    topic = _make_topic("krankenversicherung")

    service = LinkDocumentTopicService(
        document_repository=FakeDocumentRepository([stored]),
        hub_document_repository=FakeHubDocumentRepository(
            [_make_hub_document("doc-1", "data/raw/a.pdf")]
        ),
        hub_topic_repository=FakeHubTopicRepository([topic]),
        link_repository=link_repo,
    )

    created = service.sync_links()
    found = service.find_by_topic_key(topic.topic_key)

    assert len(created) == 1
    assert len(found) == 1
    assert found[0].topic_key == topic.topic_key
