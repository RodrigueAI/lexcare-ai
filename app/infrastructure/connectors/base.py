# app/infrastructure/connectors/base.py
from __future__ import annotations

from abc import ABC, abstractmethod

from app.domain.source import SourceDefinition
from app.domain.source_artifact import SourceArtifact


class ConnectorError(RuntimeError):
    pass


class ConnectorConfigError(ConnectorError):
    pass


class ConnectorFetchError(ConnectorError):
    pass


class SourceConnector(ABC):
    def __init__(self, source: SourceDefinition) -> None:
        self.source = source

    @abstractmethod
    def fetch(self) -> list[SourceArtifact]:
        raise NotImplementedError
