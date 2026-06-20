from __future__ import annotations

from unittest.mock import Mock

from app.api.schemas import QueryResponse
from app.services.rag_service import RAGService


def test_answer_calls_retriever_and_generation_services() -> None:
    retriever_service = Mock()
    generation_service = Mock()

    retrieved_chunks = [Mock(), Mock()]
    retriever_service.retrieve.return_value = retrieved_chunks

    generated = Mock()
    generated.answer = "Pflegegrad 3 bedeutet ..."
    generated.sources = [
        {
            "document_id": "doc-1",
            "chunk_id": "chunk-1",
            "source": "SGB_11.pdf",
        }
    ]
    generation_service.generate.return_value = generated

    service = RAGService(
        retriever_service=retriever_service,
        generation_service=generation_service,
    )

    result = service.answer("Was ist Pflegegrad 3?", top_k=5)

    assert isinstance(result, QueryResponse)
    assert result.question == "Was ist Pflegegrad 3?"
    assert result.answer == "Pflegegrad 3 bedeutet ..."
    assert len(result.sources) == 1
    assert result.sources[0].document_id == "doc-1"
    assert result.sources[0].chunk_id == "chunk-1"
    assert result.sources[0].source == "SGB_11.pdf"
    assert result.sources[0].score is None

    retriever_service.retrieve.assert_called_once_with(
        "Was ist Pflegegrad 3?",
        top_k=5,
    )
    generation_service.generate.assert_called_once_with(
        question="Was ist Pflegegrad 3?",
        chunks=retrieved_chunks,
    )


def test_answer_returns_empty_sources_when_generation_returns_none_like_sources() -> None:
    retriever_service = Mock()
    generation_service = Mock()

    retriever_service.retrieve.return_value = []

    generated = Mock()
    generated.answer = "I could not find relevant information in the available documents."
    generated.sources = []
    generation_service.generate.return_value = generated

    service = RAGService(
        retriever_service=retriever_service,
        generation_service=generation_service,
    )

    result = service.answer("Was ist Pflegegrad 3?", top_k=5)

    assert result.answer == "I could not find relevant information in the available documents."
    assert result.sources == []

    retriever_service.retrieve.assert_called_once_with(
        "Was ist Pflegegrad 3?",
        top_k=5,
    )
    generation_service.generate.assert_called_once_with(
        question="Was ist Pflegegrad 3?",
        chunks=[],
    )


def test_default_services_are_initialized() -> None:
    service = RAGService(
        retriever_service=Mock(),
        generation_service=Mock(),
    )

    assert service.retriever_service is not None
    assert service.generation_service is not None
