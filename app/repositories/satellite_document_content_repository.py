# app/repositories/satellite_document_content_repository.py
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from app.domain.warehouse import SatelliteDocumentContent


class FileSatelliteDocumentContentRepository:
    def __init__(
        self,
        storage_path: str = "data/warehouse/satellites/satellite_document_content.json",
    ) -> None:
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)

    def load_all(self) -> list[SatelliteDocumentContent]:
        if not self.storage_path.exists():
            return []

        data = json.loads(self.storage_path.read_text(encoding="utf-8"))
        return [self._from_dict(item) for item in data]

    def get(self, satellite_key: str) -> SatelliteDocumentContent | None:
        for satellite in self.load_all():
            if satellite.satellite_key == satellite_key:
                return satellite
        return None

    def find_versions(self, document_key: str) -> list[SatelliteDocumentContent]:
        return sorted(
            [satellite for satellite in self.load_all() if satellite.document_key == document_key],
            key=lambda item: item.effective_from,
        )

    def find_latest(self, document_key: str) -> SatelliteDocumentContent | None:
        versions = self.find_versions(document_key)
        if not versions:
            return None
        return versions[-1]

    def find_as_of(
        self,
        document_key: str,
        moment: datetime,
    ) -> SatelliteDocumentContent | None:
        for satellite in reversed(self.find_versions(document_key)):
            if satellite.effective_from <= moment and (
                satellite.effective_to is None or moment < satellite.effective_to
            ):
                return satellite
        return None

    def save(self, satellite: SatelliteDocumentContent) -> None:
        satellites = self.load_all()

        if any(item.satellite_key == satellite.satellite_key for item in satellites):
            return

        satellites.append(satellite)
        self._write_all(satellites)

    def update(self, satellite: SatelliteDocumentContent) -> None:
        satellites = self.load_all()
        updated = False

        for index, item in enumerate(satellites):
            if item.satellite_key == satellite.satellite_key:
                satellites[index] = satellite
                updated = True
                break

        if not updated:
            satellites.append(satellite)

        self._write_all(satellites)

    def _write_all(self, satellites: list[SatelliteDocumentContent]) -> None:
        self.storage_path.write_text(
            json.dumps(
                [self._to_dict(item) for item in satellites],
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

    def _to_dict(self, item: SatelliteDocumentContent) -> dict:
        return {
            "satellite_key": item.satellite_key,
            "document_key": item.document_key,
            "hash_diff": item.hash_diff,
            "loaded_at": item.loaded_at.isoformat(),
            "effective_from": item.effective_from.isoformat(),
            "effective_to": item.effective_to.isoformat() if item.effective_to else None,
            "is_current": item.is_current,
            "record_source": item.record_source,
            "payload": item.payload,
        }

    def _from_dict(self, data: dict) -> SatelliteDocumentContent:
        return SatelliteDocumentContent(
            satellite_key=data["satellite_key"],
            document_key=data["document_key"],
            hash_diff=data["hash_diff"],
            loaded_at=datetime.fromisoformat(data["loaded_at"]),
            effective_from=datetime.fromisoformat(data["effective_from"]),
            effective_to=(
                datetime.fromisoformat(data["effective_to"]) if data.get("effective_to") else None
            ),
            is_current=bool(data.get("is_current", True)),
            record_source=data.get("record_source", "lexcare-ai"),
            payload=data.get("payload", {}),
        )
