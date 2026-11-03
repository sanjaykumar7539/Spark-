# Architecture

```mermaid
flowchart LR
    CSV[(CSV input<br/>data/raw/events.csv)]
    BRONZE[Bronze<br/>raw schema-preserving events]
    SILVER[Silver<br/>validated and typed events]
    GOLD[Gold<br/>daily metrics]
    QUAR[Quarantine<br/>invalid records]
    AUDIT[Audit + quality<br/>JSON metadata]
    APP[Streamlit dashboard<br/>localhost:8501]
    AI[Ollama local analyzer<br/>qwen2.5:3b]
    SPARK[Spark 3.5.8<br/>local[*], client mode]

    CSV --> SPARK
    SPARK --> BRONZE
    BRONZE --> SILVER
    SILVER --> GOLD
    SILVER --> QUAR
    SPARK --> AUDIT
    GOLD --> APP
    GOLD --> AI
    AI --> APP
    BRONZE -. Parquet .-> BSTORE[(data/bronze/events)]
    SILVER -. Parquet .-> SSTORE[(data/silver/events)]
    GOLD -. Parquet .-> GSTORE[(data/gold/daily_metrics)]
```

## Runtime topology

The configured topology is a single local Spark client:

- `master_enabled: false`
- `spark_client_enabled: true`
- `worker_enabled: false`
- `worker_count: 0`
- `deploy_mode: client`
- effective Spark master: `local[*]`

Docker Compose provides `pipeline` and `streamlit` services using the generated Dockerfile. There is still no standalone Spark master or worker: both services use `local[*]`.

## Data flow

1. `src/bronze.py` reads CSV files and writes the source columns to Parquet.
2. `src/silver.py` reads Bronze Parquet, trims values, converts timestamps and numeric fields, and removes invalid records.
3. `src/gold.py` reads Silver Parquet and writes daily event counts, unique users, and total amounts.
4. `src/streamlit_app.py` reads Gold and the layer outputs for previews and charts.

The default pipeline is batch. An optional Structured Streaming profile is also provided, and every persisted data layer uses Parquet.

## Ingestion controls

- A shared Spark schema prevents accidental type inference changes.
- Invalid timestamps, missing identifiers, unsupported event types, null amounts, and duplicates are excluded from Silver and written to quarantine.
- Silver and Gold are partitioned by `event_date`.
- Each batch run writes an audit record and quality report.
- The optional Structured Streaming profile uses `availableNow` processing and a durable checkpoint directory.
