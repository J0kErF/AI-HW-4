"""Shared pytest fixtures (V3 §6.1).

External dependencies (LLM, network, filesystem of the target repo) are mocked
so tests never make real API calls (V3 §6.1 rule 7). Fixtures mirror the real
config so unit tests exercise the same code paths.
"""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest


class _FakeCompletions:
    """Stand-in for openai ``client.chat.completions`` (no network)."""

    def __init__(self, reply: str) -> None:
        self._reply = reply
        self.calls = 0

    def create(self, model, messages, temperature=0.0):  # noqa: ANN001, ANN201
        self.calls += 1
        usage = SimpleNamespace(prompt_tokens=50, completion_tokens=10)
        message = SimpleNamespace(content=self._reply)
        return SimpleNamespace(choices=[SimpleNamespace(message=message)], usage=usage)


@pytest.fixture
def fake_llm_client():  # noqa: ANN201
    """A fake OpenAI-compatible client whose replies mention `find_hook`."""
    reply = "Root cause: find_hook returns a single path.\n```diff\n- return path\n+ return [path]\n```"
    return SimpleNamespace(chat=SimpleNamespace(completions=_FakeCompletions(reply)))


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
