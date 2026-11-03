"""Project configuration and path helpers."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml


PROJECT_ROOT = Path(
    os.environ.get("PROJECT_ROOT", Path(__file__).resolve().parents[1])
).resolve()
CONFIG_PATH = PROJECT_ROOT / "config" / "project.yaml"


def load_config() -> dict[str, Any]:
    with CONFIG_PATH.open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)
    if not isinstance(config, dict):
        raise ValueError(f"Configuration must be a mapping: {CONFIG_PATH}")
    ollama = config.setdefault("ai_integration", {})
    if os.environ.get("OLLAMA_BASE_URL"):
        ollama["base_url"] = os.environ["OLLAMA_BASE_URL"]
    return config


def configured_path(layer: str, dataset: str) -> Path:
    return PROJECT_ROOT / "data" / layer / dataset


def require_enabled(config: dict[str, Any], section: str, key: str) -> None:
    if not config.get(section, {}).get(key, False):
        raise RuntimeError(f"Required configuration flag {section}.{key} is disabled")
