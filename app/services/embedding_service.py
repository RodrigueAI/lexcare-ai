from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from langchain_openai import AzureOpenAIEmbeddings, OpenAIEmbeddings

from app.core.config import Settings, get_settings


class EmbeddingService:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self._embeddings = self._build_embeddings()

    @property
    def embedding_function(self) -> Any:
        return self._embeddings

    def _build_embeddings(self) -> AzureOpenAIEmbeddings | OpenAIEmbeddings:
        is_azure = (self.settings.azure_openai_api_type or "").lower() == "azure"
        if is_azure:
            if not self.settings.azure_openai_endpoint:
                raise ValueError("AZURE_OPENAI_ENDPOINT is required for Azure OpenAI.")

            if not self.settings.azure_openai_api_version:
                raise ValueError("AZURE_OPENAI_API_VERSION is required for Azure OpenAI.")

            deployment = (
                self.settings.azure_openai_embeddings_name
                or self.settings.azure_openai_deployment_name
            )

            if not deployment:
                raise ValueError(
                    "AZURE_OPENAI_EMBEDDINGS_NAME or AZURE_OPENAI_DEPLOYMENT_NAME is required for Azure OpenAI."
                )

            api_key = self.settings.azure_openai_api_key
            if not api_key:
                raise ValueError("AZURE_OPENAI_API_KEY is required for Azure OpenAI.")

            return AzureOpenAIEmbeddings(
                azure_endpoint=self.settings.azure_openai_endpoint,
                azure_deployment=deployment,
                api_key=api_key,
                api_version=self.settings.azure_openai_api_version,
            )

        api_key = self.settings.azure_openai_api_key
        if not api_key:
            raise ValueError("OPENAI_API_KEY is required.")

        return OpenAIEmbeddings(
            model=self.settings.embedding_model,
            api_key=api_key,
        )

    def embed_documents(self, texts: Sequence[str]) -> list[list[float]]:
        return self._embeddings.embed_documents(list(texts))

    def embed_query(self, query: str) -> list[float]:
        return self._embeddings.embed_query(query)
