# app/infrastructure/connectors/api_connector.py
from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

import requests

from app.domain.source_artifact import SourceArtifact
from app.infrastructure.connectors.base import ConnectorFetchError, SourceConnector


class ApiConnector(SourceConnector):
    def fetch(self) -> list[SourceArtifact]:
        metadata = self.source.metadata
        endpoint = metadata.get("endpoint")
        if not endpoint:
            raise ConnectorFetchError(f"Source '{self.source.source_id}' is missing 'endpoint'.")

        headers = metadata.get("headers", {})
        params = metadata.get("params", {})
        timeout = metadata.get("timeout_seconds", 30)
        items_key = metadata.get("items_key", "items")
        title_key = metadata.get("title_key", "title")
        uri_key = metadata.get("uri_key", "uri")
        content_key = metadata.get("content_key", "content")
        metadata_key = metadata.get("metadata_key", "metadata")

        try:
            response = requests.get(
                endpoint,
                headers=headers,
                params=params,
                timeout=timeout,
            )
            response.raise_for_status()
            payload = response.json()
        except Exception as exc:
            raise ConnectorFetchError(
                f"Failed to fetch API source '{self.source.source_id}'."
            ) from exc

        items = self._extract_items(payload, items_key)
        artifacts: list[SourceArtifact] = []

        for item in items:
            if not isinstance(item, dict):
                continue

            content = item.get(content_key) or ""
            if not content:
                content = self._stringify_item(item)

            artifacts.append(
                SourceArtifact(
                    source_id=self.source.source_id,
                    source_type=self.source.source_type,
                    title=item.get(title_key),
                    uri=str(item.get(uri_key) or endpoint),
                    content=content.strip(),
                    retrieved_at=datetime.now(UTC),
                    metadata={
                        "endpoint": endpoint,
                        "raw_item": item,
                        "item_metadata": item.get(metadata_key, {}),
                    },
                )
            )

        return artifacts

    def _extract_items(self, payload: Any, items_key: str) -> list[Any]:
        if isinstance(payload, list):
            return payload

        if isinstance(payload, dict):
            items = payload.get(items_key)
            if isinstance(items, list):
                return items

        return []

    def _stringify_item(self, item: dict[str, Any]) -> str:
        return "\n".join(f"{key}: {value}" for key, value in item.items())
