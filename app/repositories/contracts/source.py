from __future__ import annotations

from typing import Protocol

from app.domain.source import SourceDefinition


class SourceRegistryProtocol(Protocol):
    def list_sources(self) -> list[SourceDefinition]: ...
    def get(self, source_id: str) -> SourceDefinition | None: ...
