from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient

from app.api.schemas import QueryResponse, SourceItem
from app.domain.models import DocumentMetadata, StoredDocument
from app.main import create_app


class FakeRAGService:
    def answer(self, question: str, top_k: int = 5) -> QueryResponse:
        return QueryResponse(
            question=question,
            answer=(
                "Pflegegrad 3 bedeutet schwere Beeinträchtigungen der Selbständigkeit "
                "oder der Fähigkeiten."
            ),
            sources=[
                SourceItem(
                    document_id="demo-doc-1",
                    chunk_id="demo-chunk-1",
                    source="SGB_11.pdf",
                    score=0.99,
                )
            ],
        )


class FakeIngestionService:
    def ingest_pdf_bytes(
        self,
        *,
        file_name: str,
        content: bytes,
        source: str,
        document_type: str,
        topic: str,
    ) -> StoredDocument:
        metadata = DocumentMetadata(
            source=source,
            document_type=document_type,
            topic=topic,
            created_at=datetime.now(UTC),
            extra={
                "filename": file_name,
                "page_count": 1,
            },
        )

        return StoredDocument(
            document_id="fake-doc-id",
            source_path=f"data/raw/uploads/{file_name}",
            text="fake extracted text",
            metadata=metadata,
        )


class FakeDocumentRepository:
    def __init__(self) -> None:
        metadata_1 = DocumentMetadata(
            source="gesetze-im-internet",
            document_type="law",
            topic="krankenversicherung",
            created_at=datetime.now(UTC),
            extra={
                "filename": "SGB_5.pdf",
                "page_count": 568,
            },
        )

        metadata_2 = DocumentMetadata(
            source="gesetze-im-internet",
            document_type="law",
            topic="pflegeversicherung",
            created_at=datetime.now(UTC),
            extra={
                "filename": "SGB_11.pdf",
                "page_count": 177,
            },
        )

        self._documents = {
            "doc-1": StoredDocument(
                document_id="doc-1",
                source_path="data/raw/gesetze_im_internet/SGB_5.pdf",
                text="sample text for SGB V",
                metadata=metadata_1,
            ),
            "doc-2": StoredDocument(
                document_id="doc-2",
                source_path="data/raw/gesetze_im_internet/SGB_11.pdf",
                text="sample text for SGB XI",
                metadata=metadata_2,
            ),
        }

    def list_documents(self):
        return list(self._documents.values())

    def read(self, document_id: str):
        if document_id not in self._documents:
            raise FileNotFoundError(document_id)
        return self._documents[document_id]


@pytest.fixture()
def app():
    application = create_app()
    yield application
    application.dependency_overrides.clear()


@pytest.fixture()
def client(app):
    return TestClient(app)


@pytest.fixture()
def fake_rag_service():
    return FakeRAGService()


@pytest.fixture()
def fake_ingestion_service():
    return FakeIngestionService()


@pytest.fixture()
def fake_document_repository():
    return FakeDocumentRepository()
