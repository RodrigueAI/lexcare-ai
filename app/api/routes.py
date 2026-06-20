from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from app.api.schemas import (
    DocumentDetailResponse,
    DocumentIngestionResponse,
    DocumentSummaryResponse,
    QueryRequest,
    QueryResponse,
)
from app.dependencies.container import (
    get_document_repository,
    get_ingestion_service,
    get_rag_service,
)
from app.domain.models import StoredDocument
from app.repositories.document_repository import DocumentRepository
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


def _document_to_summary(document: StoredDocument) -> DocumentSummaryResponse:
    extra = document.metadata.extra
    filename = str(extra.get("filename", Path(document.source_path).name))
    page_count = int(extra.get("page_count", 0))

    return DocumentSummaryResponse(
        document_id=document.document_id,
        filename=filename,
        source=document.metadata.source,
        document_type=document.metadata.document_type,
        topic=document.metadata.topic,
        source_path=document.source_path,
        page_count=page_count,
        text_length=len(document.text),
        created_at=document.metadata.created_at,
    )


def _document_to_detail(document: StoredDocument) -> DocumentDetailResponse:
    summary = _document_to_summary(document)
    return DocumentDetailResponse(
        **summary.model_dump(),
        text_preview=document.text[:2000],
    )


@router.get("/documents", summary="List ingested documents")
async def list_documents(
    repository: Annotated[DocumentRepository, Depends(get_document_repository)],
) -> list[DocumentSummaryResponse]:
    documents = repository.list_documents()
    return [_document_to_summary(document) for document in documents]


@router.get("/documents/{document_id}", summary="Get document details")
async def get_document(
    document_id: str,
    repository: Annotated[DocumentRepository, Depends(get_document_repository)],
) -> DocumentDetailResponse:
    try:
        document = repository.read(document_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Document not found.") from exc

    return _document_to_detail(document)
