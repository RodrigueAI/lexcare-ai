# app/domain/warehouse.py
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class HubSource:
    source_key: str
    source_id: str
    source_name: str
    created_at: datetime
