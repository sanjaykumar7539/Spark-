# Spark Medallion Project

Configurable Apache Spark medallion architecture demonstration for local Windows execution.

The batch pipeline reads CSV input into the **Bronze** layer, cleans and types it into **Silver**, and produces aggregated business metrics in **Gold**. All layers are persisted as Parquet.

The included sample dataset is [data/raw/events.csv](data/raw/events.csv). It contains 1,000 deterministic January 2026 event records across purchase, refund, login, and view types. The dashboard uses manual refresh so long-running AI analysis is not interrupted.

The ingestion path includes schema enforcement, validation and quarantine, date partitioning, audit and quality metadata, incremental checkpoints, and an optional Structured Streaming mode.

The dashboard supports Power BI-style product cross-filtering: click a product bar to update KPIs, trends, tables, and the AI analysis scope, then clear the filter to return to the full dataset.

See [HOWTORUN.md](HOWTORUN.md) for the exact setup and execution steps.
