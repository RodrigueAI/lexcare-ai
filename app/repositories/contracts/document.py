# app/repositories/contracts/document.py
from __future__ import annotations

from typing import Protocol

from app.domain.models import LoadedDocument, StoredDocument


class DocumentWriteRepositoryProtocol(Protocol):
    def save(self, document: LoadedDocument) -> StoredDocument: ...


class DocumentReadRepositoryProtocol(Protocol):
    def read(self, document_id: str) -> StoredDocument: ...


class DocumentListRepositoryProtocol(Protocol):
    def list_documents(self) -> list[StoredDocument]: ...


class DocumentIngestionRepositoryProtocol(
    DocumentWriteRepositoryProtocol,
    DocumentReadRepositoryProtocol,
    DocumentListRepositoryProtocol,
    Protocol,
):
    pass
