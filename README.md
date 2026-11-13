# Spark Medallion Data Pipeline

A configurable Apache Spark project that demonstrates an end-to-end medallion architecture for event data. It includes a batch processing pipeline, optional structured streaming ingestion, and a Streamlit-based dashboard for data exploration and local AI analysis.

## Overview

This project ingests sample event data, processes it through Bronze, Silver, and Gold layers, and exposes the output through a lightweight analytics dashboard. The design follows common lakehouse patterns and is intended as a practical reference for building data pipelines with Apache Spark in local or containerized environments.

```text
CSV Input → Bronze → Silver → Gold → Streamlit Dashboard
                     └────→ Quarantine
```

### Pipeline layers
- Bronze: preserves raw source data in Parquet format.
- Silver: validates, cleans, and enriches records.
- Gold: aggregates daily metrics for reporting and analytics.
- Quarantine: stores invalid or rejected records for investigation.

## Why this project

- Demonstrates a real medallion architecture using Apache Spark.
- Shows how to enforce schema and data quality checks.
- Includes reproducible sample data and batch execution.
- Provides a local dashboard for visual exploration.
- Supports Docker-based execution for simplified setup.

## Features

- Local Apache Spark processing using `local[*]` client mode
- Bronze, Silver, and Gold data layers stored as Parquet
- Schema enforcement and invalid-record quarantine
- Date-partitioned outputs and audit/quality reporting
- Optional Structured Streaming ingestion profile
- Streamlit dashboard with layer previews, charts, and filtering
- Optional local AI analysis via Ollama in Docker Compose

## Repository structure

```text
Spark-/
├── config/                 # Declarative Spark/project configuration
├── data/                   # Generated datasets and checkpoints
├── scripts/                # Setup and execution PowerShell scripts
├── src/                    # Pipeline and dashboard source code
├── .env.example            # Example environment configuration
├── ARCHITECTURE.md         # Architecture overview
├── HOWTORUN.md             # Setup and execution guide
├── TROUBLESHOOTING.md      # Common issues and fixes
├── Dockerfile              # Container definition for runtime
├── docker-compose.yml      # Local service orchestration
├── requirements.txt        # Python dependencies
├── LICENSE                 # Apache License 2.0
├── README.md               # Project documentation
└── .gitignore              # Git ignore rules
```

## Prerequisites

### Local environment
- Windows 10 or later
- Python 3.11
- Java 17
- Apache Spark 3.5.8 with Hadoop 3 support
- A writable `SPARK_HOME` path, unless Spark is already on `PATH`

### Docker environment
- Docker Desktop installed and running

## Quick start

For full setup details, see [HOWTORUN.md](HOWTORUN.md).

### Windows setup

Open PowerShell in the project root and configure Java and Spark:

```powershell
$env:JAVA_HOME = "C:\Program Files\Java\jdk-17"
$env:SPARK_HOME = "C:\spark\spark-3.5.8-bin-hadoop3"
$env:Path = "$env:SPARK_HOME\bin;$env:Path"
```

Then run:

```powershell
.\scripts\setup_windows.ps1
.\.venv\Scripts\Activate.ps1
.\scripts\run_pipeline.ps1
streamlit run .\src\streamlit_app.py
```

Open http://localhost:8501 to view the dashboard.

## Docker Compose

Start the project with Docker Compose:

```powershell
docker compose up --build
```

The dashboard is served at http://localhost:8501. For optional Ollama AI analysis and streaming workflows, refer to [HOWTORUN.md](HOWTORUN.md).

## Data flow

1. Raw CSV input is read and stored in Bronze.
2. Bronze data is validated and transformed into Silver.
3. Silver records are aggregated into Gold metrics.
4. Results are displayed through the Streamlit application.
5. Invalid records are sent to quarantine for review.

## Configuration

The project uses a declarative configuration under `config/` to govern runtime behavior. Common environment variables include:

- `SPARK_HOME`
- `JAVA_HOME`
- `SPARK_MASTER` (defaults to `local[*]`)
- `PROJECT_ROOT`

## Documentation

- [HOWTORUN.md](HOWTORUN.md) — environment setup, execution steps, Docker usage, and streaming instructions
- [ARCHITECTURE.md](ARCHITECTURE.md) — runtime topology and system design
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) — common issues and fixes

## License

This project is licensed under the [Apache License 2.0](LICENSE).

## Contributing

Contributions are welcome. If you plan to improve the pipeline, add validation logic, or expand the dashboard, please open an issue or submit a pull request with a clear description of the change.

## Acknowledgements

This project is designed to provide a practical example of medallion architecture patterns using Apache Spark and local analytics tooling.
