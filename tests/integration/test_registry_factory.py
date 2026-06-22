from __future__ import annotations

from pathlib import Path

from app.infrastructure.connectors import ConnectorFactory, FileConnector
from app.repositories.source_registry import SourceRegistry


def test_registry_and_factory_work_together(tmp_path: Path) -> None:
    registry_file = tmp_path / "source_registry.yaml"
    registry_file.write_text(
        """
sources:
  - source_id: test-files
    name: Test Files
    source_type: file
    metadata:
      root_path: data/raw/test
      file_pattern: "*.pdf"
""",
        encoding="utf-8",
    )

    registry = SourceRegistry(registry_path=str(registry_file))
    source = registry.get("test-files")

    assert source is not None

    connector = ConnectorFactory.create(source)

    assert isinstance(connector, FileConnector)
