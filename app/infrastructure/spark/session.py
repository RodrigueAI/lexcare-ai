from __future__ import annotations

from pyspark.sql import SparkSession


class SparkSessionFactory:
    @staticmethod
    def create(
        app_name: str = "LexCare AI",
        master: str = "local[*]",
    ) -> SparkSession:
        return (
            SparkSession.builder.appName(app_name)
            .master(master)
            .config("spark.sql.session.timeZone", "UTC")
            .config("spark.sql.execution.arrow.pyspark.enabled", "false")
            .getOrCreate()
        )
