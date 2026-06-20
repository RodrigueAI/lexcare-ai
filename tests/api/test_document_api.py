from app.dependencies.container import (
    get_document_repository,
    get_ingestion_service,
)


def test_documents_list_endpoint(app, fake_document_repository):
    from fastapi.testclient import TestClient

    app.dependency_overrides[get_document_repository] = lambda: fake_document_repository
    client = TestClient(app)

    response = client.get("/api/documents")

    assert response.status_code == 200
    payload = response.json()

    assert isinstance(payload, list)
    assert len(payload) == 2
    assert payload[0]["document_id"] in {"doc-1", "doc-2"}
    assert "created_at" in payload[0]


def test_document_detail_endpoint(app, fake_document_repository):
    from fastapi.testclient import TestClient

    app.dependency_overrides[get_document_repository] = lambda: fake_document_repository
    client = TestClient(app)

    response = client.get("/api/documents/doc-1")

    assert response.status_code == 200
    payload = response.json()

    assert payload["document_id"] == "doc-1"
    assert payload["filename"] == "SGB_5.pdf"
    assert isinstance(payload["text_preview"], str)


def test_document_detail_not_found(app, fake_document_repository):
    from fastapi.testclient import TestClient

    app.dependency_overrides[get_document_repository] = lambda: fake_document_repository
    client = TestClient(app)

    response = client.get("/api/documents/does-not-exist")

    assert response.status_code == 404
    assert response.json()["detail"] == "Document not found."


def test_document_upload_happy_path(app, fake_ingestion_service):
    from fastapi.testclient import TestClient

    app.dependency_overrides[get_ingestion_service] = lambda: fake_ingestion_service
    client = TestClient(app)

    response = client.post(
        "/api/documents",
        files={"file": ("SGB_5.pdf", b"%PDF-1.4 fake", "application/pdf")},
        data={
            "source": "gesetze-im-internet",
            "document_type": "law",
            "topic": "krankenversicherung",
        },
    )

    assert response.status_code == 200
    payload = response.json()

    assert payload["status"] == "ingested"
    assert payload["document_id"] == "fake-doc-id"
    assert payload["source"] == "gesetze-im-internet"
    assert payload["document_type"] == "law"
    assert payload["topic"] == "krankenversicherung"


def test_document_upload_rejects_non_pdf(client):
    response = client.post(
        "/api/documents",
        files={"file": ("notes.txt", b"hello", "text/plain")},
        data={
            "source": "gesetze-im-internet",
            "document_type": "law",
            "topic": "krankenversicherung",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Only PDF files are supported."
