from __future__ import annotations

from app.domain.source import SourceDefinition
from app.services.source_registry_service import SourceRegistryService


def test_register_source_writes_topics_and_topic(tmp_path):
    registry_path = tmp_path / "source_registry.yaml"
    service = SourceRegistryService(registry_path=str(registry_path))

    source = service.register_source(
        source_id="gesetze-im-internet",
        name="Gesetze im Internet",
        source_type="file",
        metadata={
            "root_path": "data/raw/gesetze_im_internet",
            "document_type": "law",
            "topics": ["healthcare-law", "healthcare-policy"],
        },
    )

    assert source.metadata["topics"] == ["healthcare-law", "healthcare-policy"]
    assert source.metadata["topic"] == "healthcare-law"

    loaded = service.get("gesetze-im-internet")
    assert loaded is not None
    assert loaded.source_id == "gesetze-im-internet"


def test_upsert_source_updates_existing_entry(tmp_path):
    registry_path = tmp_path / "source_registry.yaml"
    service = SourceRegistryService(registry_path=str(registry_path))

    first = SourceDefinition(
        source_id="gba",
        name="GBA",
        source_type="rss",
        metadata={"topics": ["healthcare-regulation"]},
    )
    second = SourceDefinition(
        source_id="gba",
        name="Gemeinsamer Bundesausschuss",
        source_type="rss",
        metadata={"topics": ["healthcare-regulation", "policy"]},
    )

    service.upsert_source(first)
    service.upsert_source(second)

    loaded = service.get("gba")
    assert loaded is not None
    assert loaded.name == "Gemeinsamer Bundesausschuss"
    assert loaded.metadata["topics"] == ["healthcare-regulation", "policy"]


def test_register_sources_prevents_duplicate_ids(tmp_path):
    registry_path = tmp_path / "source_registry.yaml"
    service = SourceRegistryService(registry_path=str(registry_path))

    service.register_sources(
        [
            SourceDefinition(
                source_id="bundestag",
                name="Bundestag",
                source_type="api",
                metadata={"topic": "legislation"},
            ),
            SourceDefinition(
                source_id="bundestag",
                name="Bundestag Open Data",
                source_type="api",
                metadata={"topics": ["legislation", "parliament"]},
            ),
        ]
    )

    loaded = service.get("bundestag")
    assert loaded is not None
    assert loaded.name == "Bundestag Open Data"
    assert loaded.metadata["topics"] == ["legislation", "parliament"]
