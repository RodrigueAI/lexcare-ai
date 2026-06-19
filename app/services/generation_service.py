# app/services/generation_service.py
from __future__ import annotations

from typing import Any

from langchain_openai import AzureChatOpenAI

from app.core.config import Settings, get_settings
from app.domain.models import DocumentChunk, GeneratedAnswer
from app.prompts import RAG_PROMPT


class GenerationService:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self._llm = self._build_llm()

    def _build_llm(self) -> AzureChatOpenAI:
        if not self.settings.azure_openai_endpoint:
            raise ValueError("AZURE_OPENAI_ENDPOINT is required for Azure OpenAI.")

        if not self.settings.azure_openai_api_version:
            raise ValueError("AZURE_OPENAI_API_VERSION is required for Azure OpenAI.")

        deployment = (
            self.settings.azure_openai_chat_deployment_name
            or self.settings.azure_openai_deployment_name
        )
        if not deployment:
            raise ValueError(
                "AZURE_OPENAI_CHAT_DEPLOYMENT_NAME or AZURE_OPENAI_DEPLOYMENT_NAME is required for Azure OpenAI."
            )

        if self.settings.azure_openai_api_key is None:
            raise ValueError("AZURE_OPENAI_API_KEY is required for Azure OpenAI.")

        return AzureChatOpenAI(
            azure_endpoint=self.settings.azure_openai_endpoint,
            azure_deployment=deployment,
            api_version=self.settings.azure_openai_api_version,
            api_key=self.settings.azure_openai_api_key,
        )

    def generate(
        self,
        question: str,
        chunks: list[DocumentChunk],
    ) -> GeneratedAnswer:
        if not chunks:
            return GeneratedAnswer(
                question=question,
                answer="I could not find relevant information in the available documents.",
                sources=[],
            )

        context = self._build_context(chunks)
        sources = self._build_sources(chunks)

        messages = RAG_PROMPT.format_messages(
            context=context,
            question=question,
        )

        response = self._llm.invoke(messages)
        answer_text = getattr(response, "content", str(response)).strip()

        return GeneratedAnswer(
            question=question,
            answer=answer_text,
            sources=sources,
        )

    def _build_context(self, chunks: list[DocumentChunk]) -> str:
        parts: list[str] = []

        for chunk in chunks:
            parts.append(
                f"[source={chunk.metadata.source} | document_id={chunk.document_id} | "
                f"chunk_id={chunk.chunk_id} | chunk_index={chunk.chunk_index}]\n"
                f"{chunk.text}"
            )

        return "\n\n---\n\n".join(parts)

    def _build_sources(self, chunks: list[DocumentChunk]) -> list[dict[str, Any]]:
        sources: list[dict[str, Any]] = []

        for chunk in chunks:
            sources.append(
                {
                    "document_id": chunk.document_id,
                    "chunk_id": chunk.chunk_id,
                    "chunk_index": chunk.chunk_index,
                    "source": chunk.metadata.source,
                    "document_type": chunk.metadata.document_type,
                    "topic": chunk.metadata.topic,
                    "source_path": chunk.source_path,
                }
            )

        return sources
