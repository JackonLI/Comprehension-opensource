from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

load_dotenv()


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _split_env_list(raw_value: Optional[str]) -> list[str]:
    if not raw_value:
        return []
    return [item.strip() for item in raw_value.split(",") if item.strip()]


def _first_env(*names: str) -> Optional[str]:
    for name in names:
        value = os.getenv(name)
        if value:
            return value
    return None


def resolve_data_root(explicit_root: Optional[str] = None) -> Path:
    if explicit_root:
        path = Path(explicit_root).expanduser().resolve()
        if not path.exists():
            raise FileNotFoundError(f"Dataset root does not exist: {path}")
        return path

    root = repo_root()
    candidates = [
        root / "intent dataset",
        root / "intent datasets",
        root / "dataset",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    raise FileNotFoundError(
        "Could not locate dataset directory. Expected one of: "
        "'intent dataset', 'intent datasets', or 'dataset'."
    )


@dataclass(frozen=True)
class RuntimeConfig:
    provider: str
    model: str
    api_base_url: Optional[str]
    ws_url: Optional[str]
    api_keys: list[str]
    timeout_seconds: int
    max_retries: int
    log_level: str


def load_runtime_config(
    provider: str,
    model: str,
    api_base_url: Optional[str] = None,
    ws_url: Optional[str] = None,
) -> RuntimeConfig:
    selected_api_keys = _split_env_list(_first_env("SERAPH_API_KEYS"))
    single_key = _first_env("SERAPH_API_KEY")
    if single_key and single_key not in selected_api_keys:
        selected_api_keys.append(single_key)

    return RuntimeConfig(
        provider=provider,
        model=model,
        api_base_url=api_base_url or _first_env("SERAPH_API_BASE_URL"),
        ws_url=ws_url or _first_env("SERAPH_WS_URL"),
        api_keys=selected_api_keys,
        timeout_seconds=int(_first_env("SERAPH_TIMEOUT_SECONDS") or "180"),
        max_retries=int(_first_env("SERAPH_MAX_RETRIES") or "5"),
        log_level=(_first_env("SERAPH_LOG_LEVEL") or "INFO").upper(),
    )
