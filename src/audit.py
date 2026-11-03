"""Durable run audit and data-quality metadata."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from config import PROJECT_ROOT


def _configured_dir(config: dict[str, Any], key: str) -> Path:
    relative = config["data_pipeline"][key]
    path = PROJECT_ROOT / relative
    path.mkdir(parents=True, exist_ok=True)
    return path


def write_run_audit(
    config: dict[str, Any],
    run_id: str,
    status: str,
    counts: dict[str, int],
    error: str | None = None,
) -> None:
    payload = {
        "run_id": run_id,
        "status": status,
        "completed_at_utc": datetime.now(timezone.utc).isoformat(),
        "counts": counts,
    }
    if error:
        payload["error"] = error
    target = _configured_dir(config, "audit_dir") / f"{run_id}.json"
    target.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def write_quality_report(
    config: dict[str, Any], run_id: str, checks: dict[str, Any]
) -> None:
    target = _configured_dir(config, "quality_dir") / f"{run_id}.json"
    target.write_text(
        json.dumps({"run_id": run_id, "checks": checks}, indent=2),
        encoding="utf-8",
    )
