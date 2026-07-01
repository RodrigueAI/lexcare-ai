# app/domain/warehouse/satellites.py
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class SatelliteDocumentMetadata:
    satellite_key: str
    document_key: str
    hash_diff: str
    loaded_at: datetime
    effective_from: datetime
    effective_to: datetime | None = None
    is_current: bool = True
    record_source: str = "lexcare-ai"
    payload: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class SatelliteDocumentContent:
    satellite_key: str
    document_key: str
    hash_diff: str
    loaded_at: datetime
    effective_from: datetime
    effective_to: datetime | None = None
    is_current: bool = True
    record_source: str = "lexcare-ai"
    payload: dict[str, Any] = field(default_factory=dict)
