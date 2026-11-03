# Spark Medallion Data Pipeline

A configurable Apache Spark project that demonstrates an end-to-end medallion architecture for event data. It includes a batch data pipeline, optional Structured Streaming ingestion, and a Streamlit dashboard for exploring business metrics.

## Overview

The pipeline ingests CSV events and processes them through three data layers:

```text
CSV input → Bronze → Silver → Gold → Streamlit dashboard
                         └────→ Quarantine
```

- **Bronze** preserves the source data in Parquet format.
- **Silver** validates and transforms records into typed data; invalid records are sent to quarantine.
- **Gold** produces daily aggregate metrics for the dashboard.

The sample dataset, [`data/raw/events.csv`](data/raw/events.csv), contains 1,000 deterministic events from January 2026, including purchases, refunds, logins, and views.

## Key features

- Local Apache Spark batch processing using `local[*]` client mode.
- Bronze, Silver, and Gold data layers stored as Parquet.
- Schema enforcement, event validation, and quarantine for invalid records.
- Date-partitioned data, run audit records, data-quality reports, and incremental checkpoints.
- Optional Structured Streaming ingestion.
- Streamlit dashboard with data previews, charts, and product cross-filtering.
- Optional local AI analysis with Ollama when running through Docker Compose.

## Quick start

For full prerequisites and setup instructions, see **[HOWTORUN.md](HOWTORUN.md)**. The local Windows setup requires Python 3.11, Java 17, and Apache Spark 3.5.8 with Hadoop 3 support.

After configuring `JAVA_HOME` and `SPARK_HOME`, run these commands in PowerShell from the project directory:

```powershell
.\scripts\setup_windows.ps1
.\.venv\Scripts\Activate.ps1
.\scripts\run_pipeline.ps1
streamlit run .\src\streamlit_app.py
```

Open <http://localhost:8501> to view the dashboard. Pipeline outputs are written to `data/bronze`, `data/silver`, and `data/gold`.

## Run with Docker Compose

With Docker Desktop installed and running, start the services from the project directory:

```powershell
docker compose up --build
```

The dashboard is available at <http://localhost:8501>. See [HOWTORUN.md](HOWTORUN.md) for optional Ollama setup and Structured Streaming commands.

## Documentation

- [How to run](HOWTORUN.md) — prerequisites, setup, pipeline, dashboard, Docker, and streaming.
- [Architecture](ARCHITECTURE.md) — runtime topology and data flow.
- [Troubleshooting](TROUBLESHOOTING.md) — common setup and runtime issues.

## License

This project is licensed under the [Apache License 2.0](LICENSE).
