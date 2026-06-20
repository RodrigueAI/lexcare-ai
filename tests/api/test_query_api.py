# tests/api/test_query_api.py
from app.dependencies.container import get_rag_service
from fastapi import FastAPI

from fastapi.testclient import TestClient

from tests.conftest import FakeRAGService

def test_query_endpoint_happy_path(
    app: FastAPI,
    fake_rag_service: FakeRAGService,
) -> None:
    app.dependency_overrides[get_rag_service] = lambda: fake_rag_service
    client = TestClient(app)

    response = client.post(
        "/api/query",
        json={
            "question": "Was ist Pflegegrad 3?",
            "top_k": 5,
        },
    )

    assert response.status_code == 200
    payload = response.json()

    assert payload["question"] == "Was ist Pflegegrad 3?"
    assert "Pflegegrad 3" in payload["answer"]
    assert isinstance(payload["sources"], list)
    assert len(payload["sources"]) == 1
    assert payload["sources"][0]["source"] == "SGB_11.pdf"


def test_query_endpoint_validation_error(app: FastAPI, fake_rag_service: FakeRAGService) -> None:
    app.dependency_overrides[get_rag_service] = lambda: fake_rag_service
    client = TestClient(app)

    response = client.post(
        "/api/query",
        json={
            "question": "",
            "top_k": 5,
        },
    )

    assert response.status_code == 422


def test_query_endpoint_invalid_top_k(
    client: TestClient,
) -> None:
    response = client.post(
        "/api/query",
        json={
            "question": "Was ist Pflegegrad 3?",
            "top_k": 0,
        },
    )

    assert response.status_code == 422
    