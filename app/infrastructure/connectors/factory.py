from __future__ import annotations

from app.domain.source import SourceDefinition
from app.infrastructure.connectors.api_connector import ApiConnector
from app.infrastructure.connectors.base import ConnectorConfigError, SourceConnector
from app.infrastructure.connectors.file_connector import FileConnector
from app.infrastructure.connectors.rss_connector import RssConnector
from app.infrastructure.connectors.web_connector import WebConnector


class ConnectorFactory:
    _CONNECTOR_MAP: dict[str, type[SourceConnector]] = {
        "file": FileConnector,
        "api": ApiConnector,
        "rss": RssConnector,
        "web": WebConnector,
    }

    @classmethod
    def create(cls, source: SourceDefinition) -> SourceConnector:
        source_type = source.source_type.strip().lower()
        connector_cls = cls._CONNECTOR_MAP.get(source_type)

        if connector_cls is None:
            raise ConnectorConfigError(
                f"Unsupported connector type '{source.source_type}' for source '{source.source_id}'."
            )

        return connector_cls(source)
