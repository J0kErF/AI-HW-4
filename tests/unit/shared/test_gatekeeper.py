"""Tests for the API Gatekeeper and rate limiter (no waits, no network)."""

import pytest

from graphquest.shared.gatekeeper import ApiGatekeeper, BudgetExceededError
from graphquest.shared.rate_limiter import RateLimiter


@pytest.fixture
def rl_config() -> dict:
    return {
        "global_budget_usd": 0.01,
        "pricing_usd_per_million_tokens": {"deepseek-chat": {"input": 1.0, "output": 2.0}},
        "services": {"llm": {"requests_per_minute": 2, "max_retries": 2}},
    }


class _Clock:
    """Deterministic injectable clock; sleep advances virtual time."""

    def __init__(self) -> None:
        self.t = 0.0

    def now(self) -> float:
        return self.t

    def sleep(self, seconds: float) -> None:
        self.t += max(seconds, 0.0)


def test_execute_records_tokens_and_cost(rl_config: dict) -> None:
    """A successful call is logged with priced tokens."""
    gk = ApiGatekeeper(rl_config)
    out = gk.execute(
        "llm",
        lambda: {"usage": (1000, 1000)},
        token_extractor=lambda r: r["usage"],
        model="deepseek-chat",
    )
    assert out["usage"] == (1000, 1000)
    # 1000*1.0/1e6 + 1000*2.0/1e6 = 0.003
    assert gk.total_cost_usd == pytest.approx(0.003)


def test_budget_cap_raises(rl_config: dict) -> None:
    """Spending past the global budget cap raises BudgetExceededError."""
    gk = ApiGatekeeper(rl_config)
    gk.record_usage("llm", 5_000, 0, model="deepseek-chat")  # $0.005
    with pytest.raises(BudgetExceededError):
        gk.record_usage("llm", 10_000, 0, model="deepseek-chat")  # pushes to $0.015 > $0.01


def test_retry_then_fail_is_recorded(rl_config: dict) -> None:
    """A persistently failing call retries then raises, logging a failed record."""
    gk = ApiGatekeeper(rl_config)

    def boom() -> None:
        raise ValueError("transient")

    with pytest.raises(RuntimeError, match="failed after 2 retries"):
        gk.execute("llm", boom)
    assert gk.get_queue_status().total_calls == 1
    assert gk._ledger[-1].ok is False


def test_rate_limiter_blocks_when_window_full() -> None:
    """The 3rd call within a minute (limit 2) blocks until the window clears."""
    clock = _Clock()
    rl = RateLimiter({"llm": {"requests_per_minute": 2}}, now=clock.now, sleep=clock.sleep)
    assert rl.acquire("llm") == 0
    assert rl.acquire("llm") == 0
    assert rl.acquire("llm") == 1  # had to block once
    assert clock.t >= 60.0
