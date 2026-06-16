"""Shared pytest fixtures (V3 §6.1).

External dependencies (LLM, network, filesystem of the target repo) are mocked
so tests never make real API calls (V3 §6.1 rule 7). Fixtures mirror the real
config so unit tests exercise the same code paths.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest


@pytest.fixture
def rate_limits() -> dict:
    """Minimal rate-limit/budget config block for gatekeeper tests."""
    return {
        "version": "1.00",
        "global_budget_usd": 1.50,
        "pricing_usd_per_million_tokens": {"deepseek-chat": {"input": 0.27, "output": 1.10}},
        "services": {"default": {"requests_per_minute": 30, "max_retries": 3}},
        "queue": {"max_depth": 64, "backpressure": "block"},
    }


@pytest.fixture
def tmp_config_dir(tmp_path: Path, rate_limits: dict) -> Path:
    """A temporary ``config/`` dir with valid, version-matched JSON files."""
    (tmp_path / "setup.json").write_text(
        json.dumps({"version": "1.00", "target": {"project": "thefuck"}}), encoding="utf-8"
    )
    (tmp_path / "rate_limits.json").write_text(json.dumps(rate_limits), encoding="utf-8")
    (tmp_path / "logging_config.json").write_text(
        json.dumps({"version": "1.00", "level": "INFO", "log_dir": str(tmp_path / "logs")}),
        encoding="utf-8",
    )
    return tmp_path
