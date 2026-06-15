from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.schemas import QueryRequest, QueryResponse
from app.dependencies.container import get_rag_service
from app.services.rag_service import RAGService

router = APIRouter()


@router.get("/status", summary="API status")
async def status() -> dict[str, str]:
    return {"api": "ready"}


@router.post("/query", summary="Query the RAG assistant")
async def query(
    request: QueryRequest,
    rag_service: Annotated[RAGService, Depends(get_rag_service)],
) -> QueryResponse:
    return rag_service.answer(
        question=request.question,
        top_k=request.top_k,
    )