# app/repositories/contracts/ingestion.py
from __future__ import annotations

from typing import Protocol

from app.domain.ingestion import IngestionRecord


class IngestionIndexRepositoryProtocol(Protocol):
    def load_all(self) -> list[IngestionRecord]: ...

    def find_latest(
        self,
        source_id: str,
        artifact_uri: str,
    ) -> IngestionRecord | None: ...

    def save_record(self, record: IngestionRecord) -> None: ...
