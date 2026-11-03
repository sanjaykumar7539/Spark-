"""Spark session construction for the configured local client topology."""

from __future__ import annotations

import os

from pyspark.sql import SparkSession


def create_spark_session(app_name: str) -> SparkSession:
    master = os.environ.get("SPARK_MASTER", "local[*]")
    return (
        SparkSession.builder.appName(app_name)
        .master(master)
        .config("spark.sql.session.timeZone", "UTC")
        .config("spark.sql.legacy.parquet.nanosAsLong", "false")
        .getOrCreate()
    )
