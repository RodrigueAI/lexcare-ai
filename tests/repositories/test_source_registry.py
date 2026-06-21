from pathlib import Path

from app.repositories.source_registry import SourceRegistry


def test_list_sources(
    tmp_path: Path,
):
    registry_file = tmp_path / "source_registry.yaml"

    registry_file.write_text(
        """
sources:
  - source_id: test
    name: Test Source
    source_type: file
""",
        encoding="utf-8",
    )

    registry = SourceRegistry(
        registry_path=str(registry_file),
    )

    sources = registry.list_sources()

    assert len(sources) == 1
    assert sources[0].source_id == "test"


def test_get_source(
    tmp_path: Path,
):
    registry_file = tmp_path / "source_registry.yaml"

    registry_file.write_text(
        """
sources:
  - source_id: test
    name: Test Source
    source_type: file
""",
        encoding="utf-8",
    )

    registry = SourceRegistry(
        registry_path=str(registry_file),
    )

    source = registry.get("test")

    assert source is not None
    assert source.name == "Test Source"