"""Local Ollama analyzer for the complete medallion dataset."""

from __future__ import annotations

import json
import hashlib
import urllib.error
import urllib.request
import uuid
from pathlib import Path
from typing import Any


def _frame_summary(frame: Any, max_rows: int) -> dict[str, Any]:
    summary = {
        "row_count": int(len(frame)),
        "columns": list(frame.columns),
        "null_counts": {
            column: int(frame[column].isna().sum()) for column in frame.columns
        },
    }
    if max_rows > 0:
        preview = frame.head(max_rows).copy()
        for column in preview.columns:
            preview[column] = preview[column].astype(str)
        summary["preview"] = preview.to_dict(orient="records")
    return summary


def build_summary_payload(
    bronze: Any, silver: Any, gold: Any, max_rows: int
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "analysis_version": "simple-medallion-v3",
        "pipeline_flow": "CSV input -> Bronze raw Parquet -> Silver cleaned Parquet -> Gold aggregated Parquet",
        "bronze": _frame_summary(bronze, 0),
        "silver": _frame_summary(silver, 0),
        "gold": _frame_summary(gold, max_rows),
    }
    if "event_type" in silver.columns:
        payload["silver"]["event_type_counts"] = {
            str(key): int(value)
            for key, value in silver["event_type"].value_counts().items()
        }
    if {"event_count", "unique_users", "total_amount"}.issubset(gold.columns):
        payload["gold"]["total_events"] = int(gold["event_count"].sum())
        payload["gold"]["total_unique_users"] = int(gold["unique_users"].sum())
        payload["gold"]["total_amount"] = round(
            float(gold["total_amount"].sum()), 2
        )
    return payload


def payload_fingerprint(payload: dict[str, Any]) -> str:
    serialized = json.dumps(payload, sort_keys=True, default=str).encode("utf-8")
    return hashlib.sha256(serialized).hexdigest()[:16]


def cached_summary_path(project_root: Path, fingerprint: str) -> Path:
    cache_dir = project_root / "data" / "ai"
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir / f"summary_{fingerprint}.json"


def load_cached_summary(project_root: Path, fingerprint: str) -> str | None:
    path = cached_summary_path(project_root, fingerprint)
    if not path.exists():
        return None
    cached = json.loads(path.read_text(encoding="utf-8"))
    summary = cached.get("summary")
    return summary if isinstance(summary, str) and summary.strip() else None


def save_cached_summary(
    project_root: Path, fingerprint: str, summary: str
) -> None:
    path = cached_summary_path(project_root, fingerprint)
    path.write_text(
        json.dumps({"fingerprint": fingerprint, "summary": summary}, indent=2),
        encoding="utf-8",
    )


def summarize_with_ollama(
    payload: dict[str, Any], config: dict[str, Any]
) -> str:
    settings = config["ai_integration"]
    prompt = (
        "You are a concise but complete data analyst. Explain this Spark medallion dataset "
        "in simple factual language. Do not call Silver aggregated unless the "
        "provided columns prove it. Do not invent columns, dates, users, "
        "calculations, or transformations. Use exactly these sections and no "
        "others: ## Current stage, ## Bronze, ## Silver, ## Gold, ## Simple "
        "findings. Under Current stage, state the pipeline flow and explain "
        "that the data passes through all three stages; identify Bronze as raw "
        "Parquet, Silver as cleaned/typed/validated Parquet, and Gold as "
        "aggregated Parquet. For each layer, report only its actual row count "
        "and actual column names from the data. Include verified totals, product "
        "distribution, and simple findings from the supplied data. Keep each "
        "section to 2-4 sentences or bullets. End with one sentence stating which layer is "
        "best for dashboard analysis and why. Use a fresh wording each time. "
        f"Request id: {uuid.uuid4().hex}. Data: "
        f"{json.dumps(payload, default=str)}"
    )
    request_body = json.dumps(
        {
            "model": settings["model"],
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.2, "num_predict": 700},
        }
    ).encode("utf-8")
    base_url = settings["base_url"].rstrip("/")
    request = urllib.request.Request(
        f"{base_url}/api/generate",
        data=request_body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(
            request, timeout=settings["request_timeout_seconds"]
        ) as response:
            result = json.loads(response.read().decode("utf-8"))
    except urllib.error.URLError as exc:
        raise RuntimeError(
            f"Cannot reach Ollama at {base_url}. Start Ollama and verify the model "
            f"'{settings['model']}' is available."
        ) from exc
    except json.JSONDecodeError as exc:
        raise RuntimeError("Ollama returned invalid JSON.") from exc

    answer = result.get("response")
    if not isinstance(answer, str) or not answer.strip():
        raise RuntimeError("Ollama returned an empty analysis response.")
    return answer.strip()
