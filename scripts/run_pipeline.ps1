$ErrorActionPreference = "Stop"

if (-not (Test-Path ".\.venv\Scripts\python.exe")) {
    throw "Virtual environment not found. Run .\scripts\setup_windows.ps1 first."
}
& .\.venv\Scripts\python.exe .\src\run_pipeline.py
if ($LASTEXITCODE -ne 0) {
    throw "Spark pipeline failed with exit code $LASTEXITCODE."
}
