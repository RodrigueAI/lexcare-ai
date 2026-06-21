# app/infrastructure/connectors/file_connector.py
from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from pypdf import PdfReader

from app.domain.source_artifact import SourceArtifact
from app.infrastructure.connectors.base import (
    ConnectorConfigError,
    ConnectorFetchError,
    SourceConnector,
)


class FileConnector(SourceConnector):
    def fetch(self) -> list[SourceArtifact]:
        files = self._resolve_files()
        artifacts: list[SourceArtifact] = []

        for path in files:
            if not path.is_file():
                continue

            suffix = path.suffix.lower()
            if suffix == ".pdf":
                content, extra = self._read_pdf(path)
            elif suffix in {".txt", ".md"}:
                content = path.read_text(encoding="utf-8")
                extra = {}
            elif suffix == ".json":
                content = json.dumps(
                    json.loads(path.read_text(encoding="utf-8")),
                    ensure_ascii=False,
                    indent=2,
                )
                extra = {}
            elif suffix in {".yaml", ".yml"}:
                content = path.read_text(encoding="utf-8")
                extra = {}
            else:
                continue

            artifacts.append(
                SourceArtifact(
                    source_id=self.source.source_id,
                    source_type=self.source.source_type,
                    title=path.stem,
                    uri=path.resolve().as_uri(),
                    content=content.strip(),
                    retrieved_at=datetime.now(UTC),
                    metadata={
                        "file_name": path.name,
                        "file_path": str(path),
                        "file_size_bytes": path.stat().st_size,
                        "suffix": suffix,
                        **extra,
                    },
                )
            )

        return artifacts

    def _resolve_files(self) -> list[Path]:
        metadata = self.source.metadata
        paths = metadata.get("paths")
        root_path = metadata.get("root_path")
        file_pattern = metadata.get("file_pattern", "**/*")

        resolved: list[Path] = []

        if paths:
            for item in paths:
                resolved.append(Path(item))
            return resolved

        if not root_path:
            raise ConnectorConfigError(
                f"Source '{self.source.source_id}' is missing 'root_path' or 'paths'."
            )

        root = Path(root_path)
        if not root.exists():
            raise ConnectorConfigError(f"Root path does not exist: {root_path}")

        if root.is_file():
            return [root]

        return sorted(root.glob(file_pattern))

    def _read_pdf(self, path: Path) -> tuple[str, dict[str, Any]]:
        try:
            reader = PdfReader(str(path))

            if getattr(reader, "is_encrypted", False):
                try:
                    reader.decrypt("")
                except Exception as exc:
                    raise ConnectorFetchError(f"Unable to decrypt PDF: {path}") from exc

            pages_text: list[str] = []
            for page in reader.pages:
                text = page.extract_text() or ""
                if text.strip():
                    pages_text.append(text.strip())

            return "\n\n".join(pages_text).strip(), {
                "pdf_metadata": dict(reader.metadata or {}),
                "page_count": len(reader.pages),
            }
        except ConnectorFetchError:
            raise
        except Exception as exc:
            raise ConnectorFetchError(f"Failed to read PDF: {path}") from exc
