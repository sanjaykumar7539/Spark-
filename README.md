# Spark Medallion Project

A configurable Apache Spark project that demonstrates a medallion-style data pipeline and dashboard for local development.

The batch pipeline reads event data from CSV, preserves the raw data in the **Bronze** layer, validates and types records in **Silver**, and produces daily business metrics in **Gold**. Each persisted layer is stored as Parquet.

## Pipeline at a glance

```text
CSV input → Bronze → Silver → Gold → Streamlit dashboard
                         └────→ Quarantine
```

The sample dataset, [`data/raw/events.csv`](data/raw/events.csv), contains 1,000 deterministic January 2026 events, including purchases, refunds, logins, and views.

## Features

- Apache Spark batch processing using local client mode (`local[*]`).
- Bronze, Silver, and Gold data layers, persisted as Parquet.
- Schema enforcement, event validation, and quarantine for invalid records.
- Date partitioning, run audit records, data-quality reports, and incremental checkpoints.
- Optional Structured Streaming ingestion.
- Streamlit dashboard with previews, charts, and product cross-filtering.
- Optional local Ollama analysis when running with Docker Compose.

## Quick start

See **[HOWTORUN.md](HOWTORUN.md)** for complete prerequisites and setup instructions. In brief, the local Windows setup requires Python 3.11, Java 17, and Apache Spark 3.5.8 with Hadoop 3 support.

After configuring `JAVA_HOME` and `SPARK_HOME`, use PowerShell:

```powershell
.\scripts\setup_windows.ps1
.\.venv\Scripts\Activate.ps1
.\scripts\run_pipeline.ps1
streamlit run .\src\streamlit_app.py
```

Open <http://localhost:8501> to view the dashboard. Pipeline outputs are written under `data/bronze`, `data/silver`, and `data/gold`.

### Docker Compose

With Docker Desktop installed and running, start the services from the project directory:

```powershell
docker compose up --build
```

The dashboard is available at <http://localhost:8501>. The optional Ollama setup and streaming commands are documented in [HOWTORUN.md](HOWTORUN.md).

## Documentation

- [How to run](HOWTORUN.md) — prerequisites, setup, pipeline, dashboard, Docker, and streaming.
- [Architecture](ARCHITECTURE.md) — runtime topology and data flow.
- [Troubleshooting](TROUBLESHOOTING.md) — common setup and runtime issues.

## License

This project is licensed under the [Apache License 2.0](LICENSE).
