# app/api/schemas.py
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