"""Centralized API Gatekeeper (V3 §5).

ALL external calls (LLM, network) MUST pass through :class:`ApiGatekeeper`.
It enforces rate limits read from config, queues on backpressure instead of
dropping, retries transient failures, logs every call, and keeps a token/cost
ledger that powers both the budget cap and the token-efficiency benchmark.

Implementation is intentionally stubbed (V3 docs-first workflow §2.5); the
contract below is what tests in tests/unit/shared/test_gatekeeper.py target.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any


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
    """Snapshot of the request queue (V3 §5.1)."""

    depth: int = 0
    max_depth: int = 0
    total_calls: int = 0


@dataclass
class ApiGatekeeper:
    """Single chokepoint for every external API call.

    Args:
        rate_limits: The ``rate_limits.json`` block (services, budget, pricing).
    """

    rate_limits: dict[str, Any]
    _ledger: list[CallRecord] = field(default_factory=list)

    def execute(self, service: str, api_call: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        """Run ``api_call`` through the gatekeeper.

        Checks rate limits, queues if a window is full, retries on transient
        failure, records the call, and enforces the global budget cap.

        Raises:
            RuntimeError: If the global budget cap would be exceeded.
        """
        raise NotImplementedError("Phase 2: rate-limit + retry + ledger logic")

    def record_usage(self, service: str, input_tokens: int, output_tokens: int) -> CallRecord:
        """Add a usage row to the ledger and return it (used by event-bus hooks)."""
        raise NotImplementedError("Phase 2: pricing lookup + budget check")

    def get_queue_status(self) -> QueueStatus:
        """Return current queue depth and aggregate stats."""
        raise NotImplementedError("Phase 2")

    @property
    def total_cost_usd(self) -> float:
        """Sum of recorded call costs — the live budget figure."""
        return sum(r.cost_usd for r in self._ledger)
