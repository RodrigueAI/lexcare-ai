from __future__ import annotations

from datetime import UTC, datetime

import pytest

from app.domain.models import DocumentMetadata, LoadedDocument
from app.infrastructure.spark.session import SparkSessionFactory
from app.services.spark_document_processing_service import (
    SparkDocumentProcessingService,
)


@pytest.fixture(scope="session")
def spark():
    session = SparkSessionFactory.create(
        app_name="LexCare AI Test",
        master="local[1]",
    )
    yield session
    session.stop()


def test_spark_processing_generates_chunks(spark) -> None:
    service = SparkDocumentProcessingService(
        spark=spark,
        chunk_size=50,
        chunk_overlap=10,
    )

    document = LoadedDocument(
        source_path="data/raw/gesetze_im_internet/SGB_11.pdf",
        text="Pflegegrad 3 bedeutet schwere Beeinträchtigungen der Selbständigkeit oder der Fähigkeiten.",
        metadata=DocumentMetadata(
            source="gesetze-im-internet",
            document_type="law",
            topic="pflegeversicherung",
            created_at=datetime(2024, 1, 1, tzinfo=UTC),
            extra={"filename": "SGB_11.pdf"},
        ),
    )

    result_df = service.process_documents([document])
    rows = result_df.collect()

    assert len(rows) > 0
    assert rows[0]["document_id"]
    assert rows[0]["chunk_id"]
    assert rows[0]["text"]
