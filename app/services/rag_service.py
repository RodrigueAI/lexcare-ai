# app/services/rag_service.py
from app.api.schemas import QueryResponse, SourceItem
from app.services.generation_service import GenerationService
from app.services.retriever_service import RetrieverService


class RAGService:
    def __init__(
        self,
        retriever_service: RetrieverService | None = None,
        generation_service: GenerationService | None = None,
    ) -> None:
        self.retriever_service = retriever_service or RetrieverService()
        self.generation_service = generation_service or GenerationService()

    def answer(self, question: str, top_k: int = 5) -> QueryResponse:
        retrieved_chunks = self.retriever_service.retrieve(question, top_k=top_k)

        generated = self.generation_service.generate(
            question=question,
            chunks=retrieved_chunks,
        )

        sources = [
            SourceItem(
                document_id=item["document_id"],
                chunk_id=item["chunk_id"],
                source=item["source"],
                score=None,
            )
            for item in generated.sources
        ]

        return QueryResponse(
            question=question,
            answer=generated.answer,
            sources=sources,
        )
