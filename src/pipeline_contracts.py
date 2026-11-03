"""Shared schemas and validation rules for batch and streaming ingestion."""

from __future__ import annotations

from pyspark.sql.types import DoubleType, StringType, StructField, StructType, TimestampType


EVENT_SCHEMA = StructType(
    [
        StructField("event_id", StringType(), False),
        StructField("event_time", TimestampType(), True),
        StructField("user_id", StringType(), False),
        StructField("product", StringType(), False),
        StructField("event_type", StringType(), False),
        StructField("amount", DoubleType(), True),
    ]
)


def required_columns() -> set[str]:
    return {field.name for field in EVENT_SCHEMA.fields}
