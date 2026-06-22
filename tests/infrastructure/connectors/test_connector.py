from pathlib import Path
from unittest.mock import Mock, patch

from app.domain.source import SourceDefinition
from app.infrastructure.connectors.api_connector import ApiConnector
from app.infrastructure.connectors.file_connector import FileConnector
from app.infrastructure.connectors.rss_connector import RssConnector
from app.infrastructure.connectors.web_connector import WebConnector


def test_file_connector_reads_text_file(tmp_path: Path) -> None:
    file_path = tmp_path / "doc.txt"
    file_path.write_text("hello world", encoding="utf-8")

    source = SourceDefinition(
        source_id="local-files",
        name="Local Files",
        source_type="file",
        metadata={"root_path": str(tmp_path), "file_pattern": "*.txt"},
    )

    connector = FileConnector(source)
    artifacts = connector.fetch()

    assert len(artifacts) == 1
    assert artifacts[0].content == "hello world"


@patch("app.infrastructure.connectors.api_connector.requests.get")
def test_api_connector_maps_items(mock_get) -> None:
    response = Mock()
    response.raise_for_status.return_value = None
    response.json.return_value = {
        "items": [
            {
                "title": "Example",
                "uri": "https://example.com/item/1",
                "content": "API content",
                "metadata": {"kind": "test"},
            }
        ]
    }
    mock_get.return_value = response

    source = SourceDefinition(
        source_id="api",
        name="API",
        source_type="api",
        metadata={"endpoint": "https://example.com/api"},
    )

    connector = ApiConnector(source)
    artifacts = connector.fetch()

    assert len(artifacts) == 1
    assert artifacts[0].title == "Example"
    assert artifacts[0].content == "API content"


@patch("app.infrastructure.connectors.rss_connector.feedparser.parse")
def test_rss_connector_maps_entries(mock_parse) -> None:
    feed = Mock()
    feed.entries = [
        Mock(
            title="Update",
            link="https://example.com/update",
            summary="RSS content",
            published="2026-06-01",
            updated="2026-06-01",
            author="Editor",
            id="entry-1",
        )
    ]
    mock_parse.return_value = feed

    source = SourceDefinition(
        source_id="rss",
        name="RSS",
        source_type="rss",
        metadata={"feed_urls": ["https://example.com/feed.xml"]},
    )

    connector = RssConnector(source)
    artifacts = connector.fetch()

    assert len(artifacts) == 1
    assert artifacts[0].title == "Update"
    assert artifacts[0].content == "RSS content"


@patch("app.infrastructure.connectors.web_connector.requests.get")
def test_web_connector_scrapes_allowed_domain(mock_get) -> None:
    response = Mock()
    response.raise_for_status.return_value = None
    response.status_code = 200
    response.headers = {"content-type": "text/html"}
    response.text = """
    <html>
      <head><title>Test Page</title></head>
      <body><article>Hello <b>world</b></article></body>
    </html>
    """
    mock_get.return_value = response

    source = SourceDefinition(
        source_id="web",
        name="Web",
        source_type="web",
        metadata={
            "urls": ["https://example.com/page"],
            "allowed_domains": ["example.com"],
        },
    )

    connector = WebConnector(source)
    artifacts = connector.fetch()

    assert len(artifacts) == 1
    assert artifacts[0].title == "Test Page"
    assert artifacts[0].content == "Hello world"
