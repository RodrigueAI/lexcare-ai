from __future__ import annotations

from typing import Protocol

from app.domain.ingestion import IngestionRecord
from app.domain.models import LoadedDocument, StoredDocument


class DocumentRepositoryProtocol(Protocol):
    def save(self, document: LoadedDocument) -> StoredDocument: ...
    def read(self, document_id: str) -> StoredDocument: ...
    def list_documents(self) -> list[StoredDocument]: ...


class IngestionIndexRepositoryProtocol(Protocol):
    def load_all(self) -> list[IngestionRecord]: ...
    def find_latest(
        self,
        source_id: str,
        artifact_uri: str,
    ) -> IngestionRecord | None: ...
    def save_record(self, record: IngestionRecord) -> None: ...
