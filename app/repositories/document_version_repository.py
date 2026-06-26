# app/repositories/document_version_repository.py
from __future__ import annotations

import json
from pathlib import Path

from app.domain.versioning import DocumentVersion


class FileDocumentVersionRepository:
    def __init__(self, storage_path: str = "data/processed/document_versions.json") -> None:
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)

    def load_all(self) -> list[DocumentVersion]:
        if not self.storage_path.exists():
            return []

        data = json.loads(self.storage_path.read_text(encoding="utf-8"))
        return [DocumentVersion.from_dict(item) for item in data]

    def find_versions(self, source_id: str, artifact_uri: str) -> list[DocumentVersion]:
        return [
            version
            for version in self.load_all()
            if version.source_id == source_id and version.artifact_uri == artifact_uri
        ]

    def find_latest(
        self,
        source_id: str,
        artifact_uri: str,
    ) -> DocumentVersion | None:
        versions = self.find_versions(source_id, artifact_uri)
        if not versions:
            return None

        return sorted(versions, key=lambda item: item.version_number)[-1]

    def save_version(self, version: DocumentVersion) -> None:
        versions = self.load_all()
        versions.append(version)
        self._write_all(versions)

    def update_version(self, version: DocumentVersion) -> None:
        versions = self.load_all()
        updated = False

        for index, item in enumerate(versions):
            if item.document_id == version.document_id:
                versions[index] = version
                updated = True
                break

        if not updated:
            versions.append(version)

        self._write_all(versions)

    def _write_all(self, versions: list[DocumentVersion]) -> None:
        self.storage_path.write_text(
            json.dumps([item.to_dict() for item in versions], indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
