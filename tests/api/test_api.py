# tests/api/test_api.py
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.schemas import QueryResponse, SourceItem
from app.dependencies.container import get_rag_service


class FakeRAGService:
    def answer(self, question: str, top_k: int = 5) -> QueryResponse:
        return QueryResponse(
            question=question,
            answer="Pflegegrad 3 bedeutet schwere Beeinträchtigungen der Selbständigkeit oder der Fähigkeiten.",
            sources=[
                SourceItem(
                    document_id="demo-doc-1",
                    chunk_id="demo-chunk-1",
                    source="SGB_11.pdf",
                    score=0.99,
                )
            ],
        )


def test_query_endpoint_happy_path(app: FastAPI) -> None:
    app.dependency_overrides[get_rag_service] = lambda: FakeRAGService()
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
    assert payload["answer"].strip() != ""
    assert len(payload["sources"]) == 1
    assert payload["sources"][0]["source"] == "SGB_11.pdf"
