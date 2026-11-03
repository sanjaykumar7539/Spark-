# How to Run

## Prerequisites

- Windows 10 or later
- Python 3.11
- Java 17 (set `JAVA_HOME`)
- Apache Spark 3.5.8 with Hadoop 3 support
- A writable `SPARK_HOME` directory, unless Spark is already available on `PATH`

The local configuration runs Spark in client mode. Docker Compose uses the same topology inside containers: `local[*]`, with no standalone Spark master or worker.

## Setup

1. Open PowerShell in this project directory.
2. Set Java and Spark paths for the current terminal:

   ```powershell
   $env:JAVA_HOME = "C:\Program Files\Java\jdk-17"
   $env:SPARK_HOME = "C:\spark\spark-3.5.8-bin-hadoop3"
   $env:Path = "$env:SPARK_HOME\bin;$env:Path"
   ```

3. Run the setup script. It creates `.venv`, installs Python dependencies, and creates sample input data:

   ```powershell
   .\scripts\setup_windows.ps1
   ```

4. Activate the environment:

   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

## Run the batch pipeline

```powershell
.\scripts\run_pipeline.ps1
```

Equivalent direct command:

```powershell
python .\src\run_pipeline.py
```

Outputs are written to:

- `data\bronze\events`
- `data\silver\events`
- `data\gold\daily_metrics`

The pipeline is idempotent for the sample data because each run overwrites its managed output directories. The generated CSV contains 1,000 records across all configured event types.

## Run Streamlit

After running the pipeline:

```powershell
streamlit run .\src\streamlit_app.py
```

Open <http://localhost:8501>. The app displays pipeline status, layer previews, and charts. Ollama integration is disabled by the supplied configuration and is not required.

## Run with Docker Compose

Prerequisite: Docker Desktop must be installed and running.

From the project directory:

```powershell
docker compose up --build
```

The `pipeline` service generates sample data and runs Bronze, Silver, and Gold. The `ollama` service provides local AI analysis. After the pipeline completes, the `streamlit` service starts at <http://localhost:8501>. Parquet output remains in the project `data` directory through the bind mount.

In another PowerShell terminal, download the configured model once:

```powershell
docker compose exec ollama ollama pull qwen2.5:3b
```

Then open <http://localhost:8501>, scroll to **AI data analysis**, and click **Generate AI summary**. Only Gold aggregate metrics are sent to Ollama.

The dashboard uses manual refresh. Click **Generate new AI analysis** whenever a fresh answer is needed; each click sends a new analysis request with fresh wording and does not reuse an old answer.

Click a bar in **Product mix** to filter the dashboard to that product. Use **Clear product filter** to restore all products.

Stop the services with:

```powershell
docker compose down
```

To rerun the batch pipeline after the dashboard is already built:

```powershell
docker compose run --rm pipeline
```

### Advanced ingestion

The pipeline now includes explicit schema enforcement, allowed-event validation, invalid-record quarantine, date-partitioned Parquet, run audit JSON, quality reports, and incremental checkpoint locations.

To run the optional Structured Streaming ingestion:

```powershell
docker compose --profile streaming run --rm streaming
```

Streaming checkpoints are stored under `data\checkpoints\streaming`. Batch audit records are stored under `data\audit`, quality reports under `data\quality`, and invalid records under `data\silver\quarantine`.

## Configuration

Edit [config\project.yaml](config/project.yaml) to review the declarative configuration. Runtime overrides can be supplied with environment variables:

- `SPARK_HOME`
- `JAVA_HOME`
- `SPARK_MASTER` (defaults to `local[*]`)
- `PROJECT_ROOT`

The checked-in configuration is authoritative for generated behavior. Dockerfile and Compose generation are enabled, while the Spark master and worker remain disabled by design.
