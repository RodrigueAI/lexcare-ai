# app/repositories/hub_document_repository.py
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from app.domain.warehouse import HubDocument


class FileHubDocumentRepository:
    def __init__(
        self,
        storage_path: str = "data/warehouse/hub_document.json",
    ) -> None:
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)

    def load_all(self) -> list[HubDocument]:
        if not self.storage_path.exists():
            return []

        data = json.loads(self.storage_path.read_text(encoding="utf-8"))
        return [
            HubDocument(
                document_key=item["document_key"],
                document_id=item["document_id"],
                source_key=item["source_key"],
                source_id=item["source_id"],
                document_name=item["document_name"],
                source_path=item["source_path"],
                created_at=datetime.fromisoformat(item["created_at"]),
            )
            for item in data
        ]

    def get(self, document_key: str) -> HubDocument | None:
        for document in self.load_all():
            if document.document_key == document_key:
                return document
        return None

    def save(self, hub_document: HubDocument) -> None:
        documents = self.load_all()

        if any(item.document_key == hub_document.document_key for item in documents):
            return

        documents.append(hub_document)
        self._write_all(documents)

    def _write_all(self, documents: list[HubDocument]) -> None:
        payload = [
            {
                "document_key": item.document_key,
                "document_id": item.document_id,
                "source_key": item.source_key,
                "source_id": item.source_id,
                "document_name": item.document_name,
                "source_path": item.source_path,
                "created_at": item.created_at.isoformat(),
            }
            for item in documents
        ]

        self.storage_path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
