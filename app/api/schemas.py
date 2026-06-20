# app/api/schemas.py
from datetime import datetime

from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    question: str = Field(..., min_length=1, description="User question to answer")
    top_k: int = Field(default=5, ge=1, le=10, description="Number of retrieved chunks")


class SourceItem(BaseModel):
    document_id: str
    chunk_id: str
    source: str | None = None
    score: float | None = None


class QueryResponse(BaseModel):
    question: str
    answer: str
    sources: list[SourceItem] = []


class DocumentIngestionResponse(BaseModel):
    document_id: str
    filename: str
    source: str
    document_type: str
    topic: str
    source_path: str
    page_count: int
    text_length: int
    status: str = "ingested"


class DocumentSummaryResponse(BaseModel):
    document_id: str
    filename: str
    source: str
    document_type: str
    topic: str
    source_path: str
    page_count: int
    text_length: int
    created_at: datetime


class DocumentDetailResponse(DocumentSummaryResponse):
    text_preview: str
