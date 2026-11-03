"""Silver layer: validate and type Bronze records."""

from __future__ import annotations

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import DoubleType

from config import configured_path, require_enabled
from pipeline_contracts import required_columns


def run(spark: SparkSession, config: dict) -> DataFrame:
    require_enabled(config, "data_pipeline", "silver_enabled")
    source = spark.read.parquet(str(configured_path("bronze", "events")))
    required = required_columns()
    missing = required.difference(source.columns)
    if missing:
        raise ValueError(f"Bronze data is missing columns: {sorted(missing)}")
    typed = source.select(
        F.trim("event_id").alias("event_id"),
        F.to_timestamp("event_time").alias("event_time"),
        F.trim("user_id").alias("user_id"),
        F.trim("product").alias("product"),
        F.trim("event_type").alias("event_type"),
        F.col("amount").cast(DoubleType()).alias("amount"),
    )
    allowed = config["data_pipeline"]["allowed_event_types"]
    valid = (
        typed
        .filter(
            F.col("event_id").isNotNull()
            & F.col("event_time").isNotNull()
            & F.col("user_id").isNotNull()
            & F.col("product").isNotNull()
            & F.col("event_type").isin(allowed)
            & F.col("amount").isNotNull()
        )
        .dropDuplicates(["event_id"])
    )
    invalid = typed.subtract(valid)
    if config["data_pipeline"]["quarantine_invalid_records"]:
        invalid.write.mode("overwrite").parquet(
            str(configured_path("silver", "quarantine"))
        )
    clean = (
        valid.withColumn("event_date", F.to_date("event_time"))
    )
    clean.write.mode("overwrite").partitionBy("event_date").parquet(
        str(configured_path("silver", "events"))
    )
    return clean
