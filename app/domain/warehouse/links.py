# app/domain/warehouse/links.py
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class LinkDocumentTopic:
    link_key: str
    document_key: str
    topic_key: str
    created_at: datetime
