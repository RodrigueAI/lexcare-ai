# app/domain/source.py
from dataclasses import dataclass, field


@dataclass(frozen=True)
class SourceDefinition:
    source_id: str
    name: str
    source_type: str

    description: str | None = None

    enabled: bool = True

    metadata: dict[str, str] = field(default_factory=dict)