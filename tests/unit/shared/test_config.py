"""Tests for the configuration manager and secret loader (V3 §7.2-§7.4)."""

from pathlib import Path

import pytest

from graphquest.shared.config import Config, get_secret


def test_dotted_get_reads_nested_value(tmp_config_dir: Path) -> None:
    """Config.get resolves a dotted path into the setup.json tree."""
    cfg = Config(config_dir=tmp_config_dir)
    assert cfg.get("target.project") == "thefuck"


def test_dotted_get_returns_default_when_missing(tmp_config_dir: Path) -> None:
    """An absent key returns the supplied default rather than raising."""
    cfg = Config(config_dir=tmp_config_dir)
    assert cfg.get("target.nonexistent", "fallback") == "fallback"


def test_get_secret_missing_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    """A missing environment secret raises with a pointer to .env.example."""
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(RuntimeError, match="env.example"):
        get_secret("OPENAI_API_KEY")


def test_get_secret_present_returns_value(monkeypatch: pytest.MonkeyPatch) -> None:
    """A set environment secret is returned verbatim."""
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    assert get_secret("OPENAI_API_KEY") == "sk-test"
