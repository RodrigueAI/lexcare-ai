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


@dataclass(frozen=True)
class HubDocument:
    document_key: str
    document_id: str
    source_key: str
    source_id: str
    document_name: str
    source_path: str
    created_at: datetime


@dataclass(frozen=True)
class HubTopic:
    topic_key: str
    topic_id: str
    topic_name: str
    created_at: datetime


@dataclass(frozen=True)
class LinkDocumentTopic:
    link_key: str
    document_key: str
    topic_key: str
    created_at: datetime
