# app/infrastructure/connectors/rss_connector.py
from __future__ import annotations

from datetime import UTC, datetime

import feedparser

from app.domain.source_artifact import SourceArtifact
from app.infrastructure.connectors.base import ConnectorFetchError, SourceConnector


class RssConnector(SourceConnector):
    def fetch(self) -> list[SourceArtifact]:
        feed_urls = self.source.metadata.get("feed_urls")
        if not feed_urls:
            raise ConnectorFetchError(f"Source '{self.source.source_id}' is missing 'feed_urls'.")

        if isinstance(feed_urls, str):
            feed_urls = [feed_urls]

        artifacts: list[SourceArtifact] = []

        for feed_url in feed_urls:
            try:
                feed = feedparser.parse(feed_url)
            except Exception as exc:
                raise ConnectorFetchError(f"Failed to parse RSS feed '{feed_url}'.") from exc

            if getattr(feed, "bozo", False) and not getattr(feed, "entries", []):
                raise ConnectorFetchError(f"Invalid RSS feed '{feed_url}'.")

            for entry in feed.entries:
                title = getattr(entry, "title", None)
                link = getattr(entry, "link", feed_url)
                summary = getattr(entry, "summary", None) or getattr(
                    entry,
                    "description",
                    "",
                )

                artifacts.append(
                    SourceArtifact(
                        source_id=self.source.source_id,
                        source_type=self.source.source_type,
                        title=title,
                        uri=link,
                        content=str(summary).strip(),
                        retrieved_at=datetime.now(UTC),
                        metadata={
                            "feed_url": feed_url,
                            "published": getattr(entry, "published", None),
                            "updated": getattr(entry, "updated", None),
                            "author": getattr(entry, "author", None),
                            "entry_id": getattr(entry, "id", None),
                        },
                    )
                )

        return artifacts
