# Troubleshooting

## `JAVA_HOME` is not set or Java cannot be found

Install a 64-bit JDK 17 and set it before starting PowerShell:

```powershell
$env:JAVA_HOME = "C:\Program Files\Java\jdk-17"
```

Verify with `java -version`.

## `SPARK_HOME` is missing

Install Spark 3.5.8 with Hadoop 3, then set:

```powershell
$env:SPARK_HOME = "C:\spark\spark-3.5.8-bin-hadoop3"
$env:Path = "$env:SPARK_HOME\bin;$env:Path"
```

The project does not start a standalone Spark service because the configured topology is local client mode.

## Docker Compose cannot connect to the engine

Start Docker Desktop and wait until it reports that the engine is running. Verify with:

```powershell
docker version
docker compose version
```

## Docker Compose dashboard does not start

The dashboard waits for the batch `pipeline` service to complete successfully. Inspect its logs:

```powershell
docker compose logs pipeline
```

Then rerun:

```powershell
docker compose up --build
```

## AI summary says the Ollama model is unavailable

Keep the Compose stack running and pull the configured model:

```powershell
docker compose exec ollama ollama pull qwen2.5:3b
```

The dashboard sends only Gold aggregate metrics to the local Ollama container. If the summary request times out, check Docker resource limits or increase `request_timeout_seconds` in `config\project.yaml`.

## AI summary repeats an old answer

Click **Generate new AI analysis**. Each click creates a new Ollama request with a fresh request id and wording instruction, so the prior answer is not reused.

## Invalid records appear in quarantine

Inspect `data\silver\quarantine`. Records are quarantined when required fields are missing, timestamps or amounts cannot be parsed, or `event_type` is not one of `purchase`, `refund`, `login`, or `view`.

## Streaming rerun does not process old files

Structured Streaming checkpoints intentionally remember processed files. To replay all raw CSV files, stop the streaming job and remove only `data\checkpoints\streaming`, then run the streaming profile again.

## Windows `winutils.exe` errors

Use a Spark distribution compatible with Windows and Hadoop 3. If Spark reports a missing Hadoop home, set `HADOOP_HOME` to a directory containing `bin\winutils.exe`, or use a maintained Windows Hadoop helper appropriate to your organization.

## `ModuleNotFoundError`

Activate the virtual environment and reinstall the declared dependencies:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -r .\requirements.txt
```

## The Streamlit dashboard has no data

Run the batch pipeline first:

```powershell
.\scripts\run_pipeline.ps1
```

Confirm that `data\gold\daily_metrics` exists and contains Parquet files.

## PowerShell blocks scripts

Use a process-scoped policy change, then rerun the script:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
```

## Spark output already exists or is stale

The pipeline overwrites its managed layer directories. Remove only the project-managed `data\bronze`, `data\silver`, and `data\gold` directories if a previous interrupted run left incompatible files, then rerun the pipeline.
