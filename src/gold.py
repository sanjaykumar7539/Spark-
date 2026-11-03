"""Gold layer: publish daily business metrics."""

from __future__ import annotations

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F

from config import configured_path, require_enabled


def run(spark: SparkSession, config: dict) -> DataFrame:
    require_enabled(config, "data_pipeline", "gold_enabled")
    source = spark.read.parquet(str(configured_path("silver", "events")))
    metrics = (
        source.withColumn("event_date", F.to_date("event_time"))
        .groupBy("event_date", "product")
        .agg(
            F.count("*").alias("event_count"),
            F.countDistinct("user_id").alias("unique_users"),
            F.round(F.sum("amount"), 2).alias("total_amount"),
        )
        .orderBy("event_date")
    )
    metrics.write.mode("overwrite").partitionBy("event_date").parquet(
        str(configured_path("gold", "daily_metrics"))
    )
    return metrics
