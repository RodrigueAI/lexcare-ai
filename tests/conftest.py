# tests/conftest.py
from collections.abc import Iterator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.main import create_app
from tests.helper import FakeDocumentRepository, FakeIngestionService, FakeRAGService


@pytest.fixture()
def app() -> Iterator[FastAPI]:
    application = create_app()
    yield application
    application.dependency_overrides.clear()


@pytest.fixture()
def client(app: FastAPI) -> TestClient:
    return TestClient(app)


@pytest.fixture()
def fake_rag_service() -> FakeRAGService:
    return FakeRAGService()


@pytest.fixture()
def fake_ingestion_service() -> FakeIngestionService:
    return FakeIngestionService()


@pytest.fixture()
def fake_document_repository() -> FakeDocumentRepository:
    return FakeDocumentRepository()
