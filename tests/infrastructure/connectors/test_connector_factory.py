from __future__ import annotations

import pytest

from app.domain.source import SourceDefinition
from app.infrastructure.connectors import (
    ApiConnector,
    ConnectorConfigError,
    ConnectorFactory,
    FileConnector,
    RssConnector,
    WebConnector,
)


def _make_source(source_type: str) -> SourceDefinition:
    return SourceDefinition(
        source_id=f"{source_type}-source",
        name=f"{source_type.title()} Source",
        source_type=source_type,
        metadata={},
    )


def test_factory_creates_file_connector() -> None:
    source = _make_source("file")

    connector = ConnectorFactory.create(source)

    assert isinstance(connector, FileConnector)
    assert connector.source == source


def test_factory_creates_api_connector() -> None:
    source = _make_source("api")

    connector = ConnectorFactory.create(source)

    assert isinstance(connector, ApiConnector)
    assert connector.source == source


def test_factory_creates_rss_connector() -> None:
    source = _make_source("rss")

    connector = ConnectorFactory.create(source)

    assert isinstance(connector, RssConnector)
    assert connector.source == source


def test_factory_creates_web_connector() -> None:
    source = _make_source("web")

    connector = ConnectorFactory.create(source)

    assert isinstance(connector, WebConnector)
    assert connector.source == source


def test_factory_rejects_unknown_connector_type() -> None:

    source = _make_source("unknown")
    with pytest.raises(
        ConnectorConfigError,
        match="Unsupported connector type",
    ):
        ConnectorFactory.create(source)
