from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import Mock, patch

import pytest
from pydantic import SecretStr

from app.core.config import Settings
from app.domain.models import DocumentChunk, DocumentMetadata
from app.services.generation_service import GenerationService


def _make_settings() -> Settings:
    return Settings.model_construct(
        azure_openai_endpoint="https://example.openai.azure.com/",
        azure_openai_api_version="2024-02-15-preview",
        azure_openai_deployment_name="gpt-4o-mini",
        azure_openai_api_key=SecretStr("fake-key"),
    )


def _make_chunk(
    *,
    document_id: str = "doc-1",
    chunk_id: str = "chunk-1",
    chunk_index: int = 0,
    source: str = "gesetze-im-internet",
    document_type: str = "law",
    topic: str = "pflegeversicherung",
    text: str = "Pflegegrad 3 bedeutet ...",
) -> DocumentChunk:
    metadata = DocumentMetadata(
        source=source,
        document_type=document_type,
        topic=topic,
        created_at=datetime(2024, 1, 1, tzinfo=UTC),
        extra={
            "filename": "SGB_11.pdf",
            "page_count": 177,
        },
    )

    return DocumentChunk(
        document_id=document_id,
        chunk_id=chunk_id,
        chunk_index=chunk_index,
        source_path="data/raw/gesetze_im_internet/SGB_11.pdf",
        text=text,
        metadata=metadata,
    )


@patch("app.services.generation_service.AzureChatOpenAI")
def test_builds_azure_llm(mock_azure_chat_openai):
    mock_llm = Mock()
    mock_azure_chat_openai.return_value = mock_llm

    service = GenerationService(settings=_make_settings())

    assert service is not None
    mock_azure_chat_openai.assert_called_once()


@patch("app.services.generation_service.AzureChatOpenAI")
def test_generate_returns_answer_and_sources(mock_azure_chat_openai):
    mock_llm = Mock()
    mock_llm.invoke.return_value = Mock(content="Pflegegrad 3 bedeutet schwere Beeinträchtigungen.")
    mock_azure_chat_openai.return_value = mock_llm

    service = GenerationService(settings=_make_settings())

    chunks = [
        _make_chunk(
            chunk_id="chunk-1",
            chunk_index=1,
            text="Pflegegrad 3 wird bei 47,5 bis unter 70 Punkten zugeordnet.",
        ),
        _make_chunk(
            chunk_id="chunk-2",
            chunk_index=2,
            text="Pflegegrad 3 ist Teil des Pflegegradsystems.",
        ),
    ]

    result = service.generate(
        question="Was ist Pflegegrad 3?",
        chunks=chunks,
    )

    assert result.question == "Was ist Pflegegrad 3?"
    assert result.answer == "Pflegegrad 3 bedeutet schwere Beeinträchtigungen."
    assert len(result.sources) == 2
    assert result.sources[0]["document_id"] == "doc-1"
    assert result.sources[0]["chunk_id"] == "chunk-1"
    assert result.sources[0]["source"] == "gesetze-im-internet"

    mock_llm.invoke.assert_called_once()


@patch("app.services.generation_service.AzureChatOpenAI")
def test_generate_returns_fallback_when_no_chunks(mock_azure_chat_openai):
    mock_azure_chat_openai.return_value = Mock()

    service = GenerationService(settings=_make_settings())

    result = service.generate(
        question="Was ist Pflegegrad 3?",
        chunks=[],
    )

    assert result.question == "Was ist Pflegegrad 3?"
    assert result.answer == ("I could not find relevant information in the available documents.")
    assert result.sources == []


def test_raises_when_endpoint_missing():
    settings = Settings.model_construct(
        azure_openai_api_version="2024-02-15-preview",
        azure_openai_deployment_name="gpt-4o-mini",
        azure_openai_api_key=SecretStr("fake-key"),
    )

    with pytest.raises(
        ValueError,
        match="AZURE_OPENAI_ENDPOINT is required",
    ):
        GenerationService(settings=settings)


def test_raises_when_api_version_missing():
    settings = Settings.model_construct(
        azure_openai_endpoint="https://example.openai.azure.com/",
        azure_openai_deployment_name="gpt-4o-mini",
        azure_openai_api_key=SecretStr("fake-key"),
    )

    with pytest.raises(
        ValueError,
        match="AZURE_OPENAI_API_VERSION is required",
    ):
        GenerationService(settings=settings)


def test_raises_when_deployment_missing():
    settings = Settings.model_construct(
        azure_openai_endpoint="https://example.openai.azure.com/",
        azure_openai_api_version="2024-02-15-preview",
        azure_openai_api_key=SecretStr("fake-key"),
    )

    with pytest.raises(
        ValueError,
        match="AZURE_OPENAI_DEPLOYMENT_NAME is required",
    ):
        GenerationService(settings=settings)


def test_raises_when_api_key_missing():
    settings = Settings.model_construct(
        azure_openai_endpoint="https://example.openai.azure.com/",
        azure_openai_api_version="2024-02-15-preview",
        azure_openai_deployment_name="gpt-4o-mini",
    )

    with pytest.raises(
        ValueError,
        match="AZURE_OPENAI_API_KEY is required",
    ):
        GenerationService(settings=settings)
