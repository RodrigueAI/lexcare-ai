# src/app/domain/models.py
from dataclasses import asdict, dataclass
from typing import Any

@dataclass(frozen=True)
class LoadedDocument:
    source_path: str
    text: str
    metadata: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

@dataclass(frozen=True)
class StoredDocument:
    document_id: str
    source_path: str
    text: str
    metadata: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)