"""Optional Structured Streaming ingestion for CSV files."""

from __future__ import annotations

import sys

from pyspark.sql import SparkSession
from pyspark.sql import functions as F

from config import PROJECT_ROOT, configured_path, load_config
from pipeline_contracts import EVENT_SCHEMA
from spark_session import create_spark_session


def main() -> int:
    config = load_config()
    if not config["data_pipeline"]["streaming_enabled"]:
        raise RuntimeError("Structured Streaming is disabled in project.yaml")
    spark: SparkSession = create_spark_session("spark-medallion-streaming")
    source = (
        spark.readStream.option("header", True)
        .schema(EVENT_SCHEMA)
        .csv(str(configured_path("raw", "")))
        .withColumn("event_date", F.to_date("event_time"))
    )
    checkpoint = PROJECT_ROOT / config["data_pipeline"]["checkpoint_dir"] / "streaming"
    query = (
        source.writeStream.format("parquet")
        .outputMode("append")
        .option("path", str(configured_path("bronze", "streaming_events")))
        .option("checkpointLocation", str(checkpoint))
        .trigger(availableNow=True)
        .start()
    )
    query.awaitTermination()
    spark.stop()
    return 0


if __name__ == "__main__":
    sys.exit(main())
