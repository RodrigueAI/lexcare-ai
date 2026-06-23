# app/domain/versioning.py
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class DocumentVersion:
    document_id: str
    source_id: str
    artifact_uri: str
    version_number: int
    content_hash: str
    effective_from: datetime
    effective_to: datetime | None = None
    is_current: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["effective_from"] = self.effective_from.isoformat()
        payload["effective_to"] = (
            self.effective_to.isoformat() if self.effective_to is not None else None
        )
        return payload

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> DocumentVersion:
        effective_from = datetime.fromisoformat(data["effective_from"])
        effective_to_raw = data.get("effective_to")
        effective_to = (
            datetime.fromisoformat(effective_to_raw) if isinstance(effective_to_raw, str) else None
        )

        return cls(
            document_id=data["document_id"],
            source_id=data["source_id"],
            artifact_uri=data["artifact_uri"],
            version_number=int(data["version_number"]),
            content_hash=data["content_hash"],
            effective_from=effective_from,
            effective_to=effective_to,
            is_current=bool(data.get("is_current", True)),
            metadata=data.get("metadata", {}),
        )
