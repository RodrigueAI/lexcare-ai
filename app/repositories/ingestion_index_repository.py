# app/repositories/ingestion_index_repository.py
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from app.domain.ingestion import IngestionRecord


class FileIngestionIndexRepository:
    def __init__(self, storage_path: str = "data/processed/ingestion_index.json") -> None:
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)

    def load_all(self) -> list[IngestionRecord]:
        if not self.storage_path.exists():
            return []

        data = json.loads(self.storage_path.read_text(encoding="utf-8"))
        return [self._from_dict(item) for item in data]

    def find_latest(
        self,
        source_id: str,
        artifact_uri: str,
    ) -> IngestionRecord | None:
        matches = [
            record
            for record in self.load_all()
            if record.source_id == source_id and record.artifact_uri == artifact_uri
        ]

        if not matches:
            return None

        return sorted(matches, key=lambda item: item.ingested_at)[-1]

    def save_record(self, record: IngestionRecord) -> None:
        records = self.load_all()
        records.append(record)
        self.storage_path.write_text(
            json.dumps([self._to_dict(item) for item in records], indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def _to_dict(self, record: IngestionRecord) -> dict:
        return {
            "source_id": record.source_id,
            "artifact_uri": record.artifact_uri,
            "content_hash": record.content_hash,
            "document_id": record.document_id,
            "ingested_at": record.ingested_at.isoformat(),
            "metadata": record.metadata,
        }

    def _from_dict(self, data: dict) -> IngestionRecord:
        return IngestionRecord(
            source_id=data["source_id"],
            artifact_uri=data["artifact_uri"],
            content_hash=data["content_hash"],
            document_id=data["document_id"],
            ingested_at=datetime.fromisoformat(data["ingested_at"]),
            metadata=data.get("metadata", {}),
        )
