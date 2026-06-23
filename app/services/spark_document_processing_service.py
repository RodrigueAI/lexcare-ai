from __future__ import annotations

import json
from typing import Any

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F
from pyspark.sql import types as T

from app.domain.models import DocumentMetadata, LoadedDocument, StoredDocument
from app.infrastructure.spark.session import SparkSessionFactory
from app.services.chunking_service import ChunkingService
from app.services.text_cleaning_service import TextCleaningService


class SparkDocumentProcessingService:
    def __init__(
        self,
        spark: SparkSession | None = None,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
    ) -> None:
        self.spark = spark or SparkSessionFactory.create()
        self.cleaning_service = TextCleaningService()
        self.chunking_service = ChunkingService(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )

        self._output_schema = T.StructType(
            [
                T.StructField("document_id", T.StringType(), False),
                T.StructField("chunk_id", T.StringType(), False),
                T.StructField("chunk_index", T.IntegerType(), False),
                T.StructField("source_path", T.StringType(), False),
                T.StructField("text", T.StringType(), False),
                T.StructField("metadata_json", T.StringType(), False),
            ]
        )

    def process_documents(self, documents: list[LoadedDocument]) -> DataFrame:
        if not documents:
            return self.spark.createDataFrame([], schema=self._output_schema)

        input_rows = [
            {
                "source_path": document.source_path,
                "text": document.text,
                "metadata_json": json.dumps(
                    document.metadata.to_dict(),
                    ensure_ascii=False,
                    default=str,
                ),
            }
            for document in documents
        ]

        input_schema = T.StructType(
            [
                T.StructField("source_path", T.StringType(), False),
                T.StructField("text", T.StringType(), False),
                T.StructField("metadata_json", T.StringType(), False),
            ]
        )

        df = self.spark.createDataFrame(input_rows, schema=input_schema)

        cleaned_df = df.withColumn(
            "clean_text",
            F.trim(
                F.regexp_replace(
                    F.regexp_replace(
                        F.regexp_replace(
                            F.col("text"),
                            r"[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F]",
                            "",
                        ),
                        r"[ \t\f\v]+",
                        " ",
                    ),
                    r"\n{3,}",
                    "\n\n",
                )
            ),
        )

        rows = cleaned_df.select("source_path", "clean_text", "metadata_json").collect()

        chunk_rows: list[dict[str, Any]] = []
        for row in rows:
            metadata_dict = json.loads(row["metadata_json"])
            metadata = DocumentMetadata.from_dict(metadata_dict)

            loaded_document = LoadedDocument(
                source_path=row["source_path"],
                text=row["clean_text"],
                metadata=metadata,
            )

            stored_document = StoredDocument(
                document_id=self._document_id_from_source_path(row["source_path"]),
                source_path=loaded_document.source_path,
                text=loaded_document.text,
                metadata=loaded_document.metadata,
            )

            chunks = self.chunking_service.split(
                document=stored_document,
                text=loaded_document.text,
            )

            for chunk in chunks:
                chunk_rows.append(
                    {
                        "document_id": chunk.document_id,
                        "chunk_id": chunk.chunk_id,
                        "chunk_index": chunk.chunk_index,
                        "source_path": chunk.source_path,
                        "text": chunk.text,
                        "metadata_json": json.dumps(
                            chunk.metadata.to_dict(),
                            ensure_ascii=False,
                            default=str,
                        ),
                    }
                )

        return self.spark.createDataFrame(chunk_rows, schema=self._output_schema)

    def _document_id_from_source_path(self, source_path: str) -> str:
        return source_path.rsplit("/", 1)[-1].replace(".", "_")
