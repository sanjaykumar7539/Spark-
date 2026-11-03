$ErrorActionPreference = "Stop"

if (-not $env:JAVA_HOME) {
    Write-Warning "JAVA_HOME is not set. Set it to a Java 17 installation before running Spark."
}
if (-not $env:SPARK_HOME) {
    Write-Warning "SPARK_HOME is not set. Set it to the Spark 3.5.8 installation before running the pipeline."
}

python -m venv .venv
& .\.venv\Scripts\python.exe -m pip install --upgrade pip
& .\.venv\Scripts\python.exe -m pip install -r .\requirements.txt
& .\.venv\Scripts\python.exe .\src\generate_sample_data.py
Write-Host "Setup complete. Activate with .\.venv\Scripts\Activate.ps1"
