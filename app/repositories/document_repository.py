# src/app/repositories/document_repository.py
from __future__ import annotations

import json
from abc import ABC, abstractmethod
from pathlib import Path
from uuid import uuid4

from app.domain.models import LoadedDocument, StoredDocument


class DocumentRepository(ABC):
    @abstractmethod
    def save(self, document: LoadedDocument) -> StoredDocument:
        raise NotImplementedError

    @abstractmethod
    def read(self, document_id: str) -> StoredDocument:
        raise NotImplementedError

    @abstractmethod
    def list_documents(self) -> list[StoredDocument]:
        raise NotImplementedError


class FileDocumentRepository(DocumentRepository):
    def __init__(self, storage_dir: str = "data/processed/documents") -> None:
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def _path_for(self, document_id: str) -> Path:
        return self.storage_dir / f"{document_id}.json"

    def save(self, document: LoadedDocument) -> StoredDocument:
        document_id = str(uuid4())

        stored = StoredDocument(
            document_id=document_id,
            source_path=document.source_path,
            text=document.text,
            metadata=document.metadata,
        )

        self._path_for(document_id).write_text(
            json.dumps(stored.to_dict(), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

        return stored

    def read(self, document_id: str) -> StoredDocument:
        path = self._path_for(document_id)

        if not path.exists():
            raise FileNotFoundError(f"Document not found: {document_id}")

        data = json.loads(path.read_text(encoding="utf-8"))
        return StoredDocument.from_dict(data)

    def list_documents(self) -> list[StoredDocument]:
        documents: list[StoredDocument] = []

        for path in sorted(self.storage_dir.glob("*.json")):
            data = json.loads(path.read_text(encoding="utf-8"))
            documents.append(StoredDocument.from_dict(data))

        return documents
