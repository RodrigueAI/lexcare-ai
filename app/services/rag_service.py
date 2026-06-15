from app.api.schemas import QueryResponse, SourceItem


class RAGService:
    def answer(self, question: str, top_k: int = 5) -> QueryResponse:
        sources = [
            SourceItem(
                document_id="demo-doc-1",
                chunk_id="demo-chunk-1",
                source="sample.pdf",
                score=0.92,
            )
        ]

        return QueryResponse(
            question=question,
            answer=(
                "This is a placeholder response from the RAG service. "
                "The retrieval and generation pipeline will be connected here next."
            ),
            sources=sources[:top_k],
        )