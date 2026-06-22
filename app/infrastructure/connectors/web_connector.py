# app/infrastructure/connectors/web_connector.py
from __future__ import annotations

from datetime import UTC, datetime
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

from app.domain.source_artifact import SourceArtifact
from app.infrastructure.connectors.base import (
    ConnectorConfigError,
    ConnectorFetchError,
    SourceConnector,
)


class WebConnector(SourceConnector):
    def fetch(self) -> list[SourceArtifact]:
        urls = self.source.metadata.get("urls")
        allowed_domains = self.source.metadata.get("allowed_domains", [])
        timeout = self.source.metadata.get("timeout_seconds", 30)

        if not urls:
            raise ConnectorConfigError(f"Source '{self.source.source_id}' is missing 'urls'.")

        if isinstance(urls, str):
            urls = [urls]

        artifacts: list[SourceArtifact] = []

        for url in urls:
            self._validate_url(url, allowed_domains)

            try:
                response = requests.get(url, timeout=timeout)
                response.raise_for_status()
            except Exception as exc:
                raise ConnectorFetchError(f"Failed to fetch URL: {url}") from exc

            html = response.text
            title, content = self._extract_content(html)

            artifacts.append(
                SourceArtifact(
                    source_id=self.source.source_id,
                    source_type=self.source.source_type,
                    title=title,
                    uri=url,
                    content=content,
                    retrieved_at=datetime.now(UTC),
                    metadata={
                        "url": url,
                        "status_code": response.status_code,
                        "content_type": response.headers.get("content-type"),
                    },
                )
            )

        return artifacts

    def _validate_url(self, url: str, allowed_domains: list[str]) -> None:
        if not allowed_domains:
            raise ConnectorConfigError(
                f"Source '{self.source.source_id}' must define 'allowed_domains' for web scraping."
            )

        netloc = urlparse(url).netloc.lower()
        allowed = any(
            netloc == domain.lower() or netloc.endswith(f".{domain.lower()}")
            for domain in allowed_domains
        )
        if not allowed:
            raise ConnectorConfigError(f"Domain not allowed for scraping: {netloc}")

    def _extract_content(self, html: str) -> tuple[str | None, str]:
        soup = BeautifulSoup(html, "html.parser")

        title = None
        if soup.title and soup.title.string:
            title = soup.title.string.strip()

        content_node = soup.find("article") or soup.find("main") or soup.body or soup
        text = content_node.get_text(separator=" ", strip=True)

        return title, self._normalize_whitespace(text)

    def _normalize_whitespace(self, text: str) -> str:
        return " ".join(text.split())
