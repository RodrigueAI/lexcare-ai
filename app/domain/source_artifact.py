# app/domain/source_artifact.py
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class SourceArtifact:
    source_id: str
    source_type: str
    title: str | None
    uri: str
    content: str
    retrieved_at: datetime
    metadata: dict[str, Any] = field(default_factory=dict)
