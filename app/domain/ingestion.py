from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class IngestionRecord:
    source_id: str
    artifact_uri: str
    content_hash: str
    document_id: str
    ingested_at: datetime
    metadata: dict[str, Any]


@dataclass(frozen=True)
class IngestionSummary:
    source_id: str
    fetched: int
    ingested: int
    skipped: int
    updated: int
    errors: int = 0
