"""Centralized API Gatekeeper (V3 §5).

ALL external calls (LLM, network) MUST pass through :class:`ApiGatekeeper`.
It enforces rate limits (blocking backpressure via :class:`RateLimiter`),
retries transient failures, logs every call, and keeps a token/cost ledger that
powers both the global budget cap and the token-efficiency benchmark.

Clock/sleep are injected through the limiter, so the whole thing is unit-tested
with a mocked ``api_call`` and no real waits or network.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from graphquest.shared.rate_limiter import RateLimiter


class BudgetExceededError(RuntimeError):
    """Raised when a call would push spend past ``global_budget_usd``."""


@dataclass
class CallRecord:
    """One logged API call for the cost/token ledger."""

    service: str
    input_tokens: int = 0
    output_tokens: int = 0
    cost_usd: float = 0.0
    retries: int = 0
    ok: bool = True


@dataclass
class QueueStatus:
    """Snapshot of gatekeeper activity (V3 §5.1)."""

    depth: int = 0
    max_depth: int = 0
    total_calls: int = 0


class ApiGatekeeper:
    """Single chokepoint for every external API call.

    Args:
        rate_limits: The ``rate_limits.json`` block (services, budget, pricing).
        limiter: Rate limiter (injected; built from config if omitted).
    """

    def __init__(self, rate_limits: dict[str, Any], limiter: RateLimiter | None = None) -> None:
        self.rate_limits = rate_limits
        self._limiter = limiter or RateLimiter(rate_limits.get("services", {}))
        self._budget = float(rate_limits.get("global_budget_usd", float("inf")))
        self._pricing = rate_limits.get("pricing_usd_per_million_tokens", {})
        self._ledger: list[CallRecord] = []
        self._blocks = 0

    def execute(
        self,
        service: str,
        api_call: Callable[..., Any],
        *args: Any,
        token_extractor: Callable[[Any], tuple[int, int]] | None = None,
        model: str | None = None,
        **kwargs: Any,
    ) -> Any:
        """Run ``api_call`` through the gatekeeper.

        Enforces the rate limit (blocking if full), checks the budget, retries
        transient failures, records the call (with tokens if ``token_extractor``
        is given), and returns the call result.

        Raises:
            BudgetExceededError: If spend is already at/over the budget cap.
        """
        if self.total_cost_usd >= self._budget:
            raise BudgetExceededError(f"Budget ${self._budget} reached")
        self._blocks += self._limiter.acquire(service)
        result, retries = self._call_with_retries(service, api_call, args, kwargs)
        tokens = token_extractor(result) if token_extractor else (0, 0)
        self.record_usage(service, *tokens, model=model, retries=retries)
        return result

    def _call_with_retries(
        self, service: str, api_call: Callable[..., Any], args: tuple, kwargs: dict
    ) -> tuple[Any, int]:
        """Call with up to ``max_retries`` attempts on transient exceptions."""
        cfg = self.rate_limits.get("services", {}).get(service, {})
        max_retries = int(cfg.get("max_retries", 3))
        last_exc: Exception | None = None
        for attempt in range(max_retries + 1):
            try:
                return api_call(*args, **kwargs), attempt
            except Exception as exc:  # noqa: BLE001 - gatekeeper records then re-raises
                last_exc = exc
        self._ledger.append(CallRecord(service=service, retries=max_retries, ok=False))
        raise RuntimeError(f"{service} call failed after {max_retries} retries") from last_exc

    def record_usage(
        self,
        service: str,
        input_tokens: int,
        output_tokens: int,
        model: str | None = None,
        retries: int = 0,
    ) -> CallRecord:
        """Price the tokens, append a ledger row, and enforce the budget.

        Raises:
            BudgetExceededError: If this call pushes total spend over the cap.
        """
        cost = self._price(input_tokens, output_tokens, model)
        record = CallRecord(service, input_tokens, output_tokens, cost, retries, ok=True)
        self._ledger.append(record)
        if self.total_cost_usd > self._budget:
            raise BudgetExceededError(
                f"Spend ${self.total_cost_usd:.4f} exceeds budget ${self._budget}"
            )
        return record

    def _price(self, input_tokens: int, output_tokens: int, model: str | None) -> float:
        """USD cost from per-million pricing; default to the sole priced model."""
        if not self._pricing:
            return 0.0
        key = model if model in self._pricing else next(iter(self._pricing))
        rates = self._pricing.get(key, {})
        return (input_tokens * rates.get("input", 0.0) + output_tokens * rates.get("output", 0.0)) / 1e6

    def get_queue_status(self) -> QueueStatus:
        """Return aggregate gatekeeper stats (blocks waited, total calls)."""
        return QueueStatus(depth=0, max_depth=self._blocks, total_calls=len(self._ledger))

    @property
    def total_cost_usd(self) -> float:
        """Sum of recorded call costs — the live budget figure."""
        return sum(r.cost_usd for r in self._ledger)
