from __future__ import annotations

from unittest.mock import Mock, patch

import pytest

from app.core.config import Settings
from app.services.embedding_service import EmbeddingService


def _azure_settings() -> Settings:
    return Settings.model_construct(
        azure_openai_api_type="azure",
        azure_openai_endpoint="https://example.openai.azure.com/",
        azure_openai_api_version="2024-02-15-preview",
        azure_openai_deployment_name="gpt-4o",
        azure_openai_embeddings_name="text-embedding-ada-002",
        azure_openai_api_key="fake-key",
        embedding_model="text-embedding-3-small",
    )


@patch("app.services.embedding_service.AzureOpenAIEmbeddings")
def test_builds_azure_embeddings(mock_embeddings):
    settings = _azure_settings()

    EmbeddingService(settings=settings)

    mock_embeddings.assert_called_once()


@patch("app.services.embedding_service.AzureOpenAIEmbeddings")
def test_embed_documents_delegates_to_embedding_model(mock_embeddings):
    fake_model = Mock()
    fake_model.embed_documents.return_value = [[0.1, 0.2]]

    mock_embeddings.return_value = fake_model

    service = EmbeddingService(settings=_azure_settings())

    result = service.embed_documents(["hello"])

    assert result == [[0.1, 0.2]]
    fake_model.embed_documents.assert_called_once_with(["hello"])


@patch("app.services.embedding_service.AzureOpenAIEmbeddings")
def test_embed_query_delegates_to_embedding_model(mock_embeddings):
    fake_model = Mock()
    fake_model.embed_query.return_value = [0.1, 0.2, 0.3]

    mock_embeddings.return_value = fake_model

    service = EmbeddingService(settings=_azure_settings())

    result = service.embed_query("What is Pflegegrad 3?")

    assert result == [0.1, 0.2, 0.3]
    fake_model.embed_query.assert_called_once_with("What is Pflegegrad 3?")


def test_raises_when_azure_endpoint_missing():
    settings = Settings.model_construct(
        azure_openai_api_type="azure",
        azure_openai_api_version="2024-02-15-preview",
        azure_openai_embeddings_name="text-embedding-ada-002",
        azure_openai_api_key="fake-key",
    )

    with pytest.raises(
        ValueError,
        match="AZURE_OPENAI_ENDPOINT is required",
    ):
        EmbeddingService(settings=settings)


def test_raises_when_api_version_missing():
    settings = Settings.model_construct(
        azure_openai_api_type="azure",
        azure_openai_endpoint="https://example.openai.azure.com/",
        azure_openai_embeddings_name="text-embedding-ada-002",
        azure_openai_api_key="fake-key",
    )

    with pytest.raises(
        ValueError,
        match="AZURE_OPENAI_API_VERSION is required",
    ):
        EmbeddingService(settings=settings)


def test_raises_when_embedding_deployment_missing():
    settings = Settings.model_construct(
        azure_openai_api_type="azure",
        azure_openai_endpoint="https://example.openai.azure.com/",
        azure_openai_api_version="2024-02-15-preview",
        azure_openai_api_key="fake-key",
    )

    with pytest.raises(
        ValueError,
        match="AZURE_OPENAI_EMBEDDINGS_NAME",
    ):
        EmbeddingService(settings=settings)


def test_raises_when_api_key_missing():
    settings = Settings.model_construct(
        azure_openai_api_type="azure",
        azure_openai_endpoint="https://example.openai.azure.com/",
        azure_openai_api_version="2024-02-15-preview",
        azure_openai_embeddings_name="text-embedding-ada-002",
    )

    with pytest.raises(
        ValueError,
        match="AZURE_OPENAI_API_KEY is required",
    ):
        EmbeddingService(settings=settings)
