# app/repositories/contracts/versioning.py
from __future__ import annotations

from typing import Protocol

from app.domain.versioning import DocumentVersion


class DocumentVersionRepositoryProtocol(Protocol):
    def load_all(self) -> list[DocumentVersion]: ...

    def find_versions(
        self,
        source_id: str,
        artifact_uri: str,
    ) -> list[DocumentVersion]: ...

    def find_latest(
        self,
        source_id: str,
        artifact_uri: str,
    ) -> DocumentVersion | None: ...

    def save_version(self, version: DocumentVersion) -> None: ...

    def update_version(self, version: DocumentVersion) -> None: ...
