"""Configuration manager (V3 §7.2, §7.3 — no hardcoded values).

Loads the versioned JSON config files from ``config/`` and exposes typed,
dotted-path access. Secrets are NOT read here — they come from environment
variables via :func:`get_secret` so they never touch a config file or the repo.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from graphquest.shared.version import assert_config_compatible

_CONFIG_DIR = Path(__file__).resolve().parents[3] / "config"


class Config:
    """Read-only view over the merged ``config/*.json`` files.

    Args:
        config_dir: Override directory (defaults to the repo ``config/``).
    """

    def __init__(self, config_dir: Path | None = None) -> None:
        self._dir = config_dir or _CONFIG_DIR
        self._setup = self._load("setup.json")
        self._rate_limits = self._load("rate_limits.json")
        self._logging = self._load("logging_config.json")
        assert_config_compatible(self._setup["version"])
        assert_config_compatible(self._rate_limits["version"])

    def _load(self, name: str) -> dict[str, Any]:
        return json.loads((self._dir / name).read_text(encoding="utf-8"))

    def get(self, dotted_key: str, default: Any = None) -> Any:
        """Return a value by dotted path, e.g. ``"target.project"``."""
        node: Any = self._setup
        for part in dotted_key.split("."):
            if not isinstance(node, dict) or part not in node:
                return default
            node = node[part]
        return node

    @property
    def rate_limits(self) -> dict[str, Any]:
        """The full rate-limit / budget configuration block."""
        return self._rate_limits

    @property
    def logging(self) -> dict[str, Any]:
        """The logging configuration block."""
        return self._logging


def get_secret(name: str) -> str:
    """Return a secret from the environment, raising if missing (V3 §7.4).

    Args:
        name: Environment variable name (e.g. ``"OPENAI_API_KEY"``).

    Raises:
        RuntimeError: If the variable is unset, with a pointer to .env.example.
    """
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"Missing secret {name!r}. Copy .env.example to .env and fill it in.")
    return value
