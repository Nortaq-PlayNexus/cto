"""Configuration management for CTO Dashboard."""

import json
import os
from pathlib import Path
from typing import Any

_DEFAULT_CONFIG_PATH = Path(__file__).parent.parent / "config" / "default.json"


def load_config(config_path: str | None = None) -> dict[str, Any]:
    path = Path(config_path) if config_path else _DEFAULT_CONFIG_PATH
    config: dict[str, Any] = {}

    if path.exists():
        with open(path) as f:
            config = json.load(f)

    env_token = os.environ.get("CTO_DASHBOARD_GITHUB_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if env_token:
        config["github_token"] = env_token

    gh_config_path = Path.home() / ".config" / "cto-dashboard" / "config.json"
    if gh_config_path.exists():
        with open(gh_config_path) as f:
            user_config = json.load(f)
        config = {**user_config, **config}

    return config
