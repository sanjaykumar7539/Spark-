"""Bronze layer: preserve source records in Parquet."""

from __future__ import annotations

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F

from config import configured_path, require_enabled
from pipeline_contracts import EVENT_SCHEMA


def run(spark: SparkSession, config: dict) -> DataFrame:
    require_enabled(config, "data_pipeline", "bronze_enabled")
    input_path = configured_path("raw", "events.csv")
    output_path = configured_path("bronze", "events")
    if not input_path.exists():
        raise FileNotFoundError(
            f"Input CSV not found at {input_path}. Run generate_sample_data.py first."
        )
    frame = spark.read.option("header", True).schema(EVENT_SCHEMA).csv(str(input_path))
    if not frame.columns:
        raise ValueError(f"Input CSV has no columns: {input_path}")
    frame = frame.withColumn("ingestion_date", F.current_date())
    frame.write.mode("overwrite").partitionBy("ingestion_date").parquet(str(output_path))
    return frame
