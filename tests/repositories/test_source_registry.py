from __future__ import annotations

from pathlib import Path

from app.repositories.source_registry import SourceRegistry


def test_list_sources(tmp_path: Path) -> None:
    registry_file = tmp_path / "source_registry.yaml"

    registry_file.write_text(
        """
sources:
  - source_id: test
    name: Test Source
    source_type: file
    description: Sample registry source
    enabled: true
    metadata:
      root_path: data/raw/test
""",
        encoding="utf-8",
    )

    registry = SourceRegistry(registry_path=str(registry_file))

    sources = registry.list_sources()

    assert len(sources) == 1
    assert sources[0].source_id == "test"
    assert sources[0].name == "Test Source"
    assert sources[0].source_type == "file"
    assert sources[0].enabled is True
    assert sources[0].metadata["root_path"] == "data/raw/test"


def test_get_source(tmp_path: Path) -> None:
    registry_file = tmp_path / "source_registry.yaml"

    registry_file.write_text(
        """
sources:
  - source_id: test
    name: Test Source
    source_type: file
    enabled: true
""",
        encoding="utf-8",
    )

    registry = SourceRegistry(registry_path=str(registry_file))

    source = registry.get("test")

    assert source is not None
    assert source.source_id == "test"
    assert source.name == "Test Source"


def test_get_source_returns_none_when_missing(tmp_path: Path) -> None:
    registry_file = tmp_path / "source_registry.yaml"
    registry_file.write_text("sources: []", encoding="utf-8")

    registry = SourceRegistry(registry_path=str(registry_file))

    assert registry.get("missing") is None
