from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from app.api.schemas import (
    DocumentIngestionResponse,
    QueryRequest,
    QueryResponse,
)
from app.dependencies.container import get_ingestion_service, get_rag_service
from app.services.ingestion_service import IngestionService
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


@router.post("/documents", summary="Ingest a PDF document")
async def ingest_document(
    file: Annotated[UploadFile, File(...)],
    source: Annotated[str, Form(..., min_length=1)],
    document_type: Annotated[str, Form(..., min_length=1)],
    topic: Annotated[str, Form(..., min_length=1)],
    ingestion_service: Annotated[IngestionService, Depends(get_ingestion_service)],
) -> DocumentIngestionResponse:
    if not file.filename:
        raise HTTPException(status_code=400, detail="Uploaded file must have a filename.")

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    content = await file.read()

    try:
        stored_document = ingestion_service.ingest_pdf_bytes(
            file_name=file.filename,
            content=content,
            source=source,
            document_type=document_type,
            topic=topic,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    page_count = int(stored_document.metadata.extra.get("page_count", 0))
    filename = str(stored_document.metadata.extra.get("filename", file.filename))

    return DocumentIngestionResponse(
        document_id=stored_document.document_id,
        filename=filename,
        source=stored_document.metadata.source,
        document_type=stored_document.metadata.document_type,
        topic=stored_document.metadata.topic,
        source_path=stored_document.source_path,
        page_count=page_count,
        text_length=len(stored_document.text),
    )
