"""Sliding-window rate limiter for the Gatekeeper (V3 §5.2, §5.3).

Per-service requests-per-minute window. When the window is full, ``acquire``
*blocks* (backpressure) until the oldest request ages out, rather than dropping
the call. Clock and sleep are injected so the limiter is unit-testable without
real wall-clock waits.
"""

from __future__ import annotations

import time
from collections import deque
from collections.abc import Callable
from typing import Any

_WINDOW_SECONDS = 60.0


class RateLimiter:
    """Block-on-limit sliding-window limiter, one window per service.

    Args:
        services: The ``services`` block from ``rate_limits.json``.
        now: Monotonic clock (injected for tests).
        sleep: Sleep function (injected for tests).
    """

    def __init__(
        self,
        services: dict[str, Any],
        now: Callable[[], float] = time.monotonic,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        self._services = services
        self._now = now
        self._sleep = sleep
        self._hits: dict[str, deque[float]] = {}

    def _rpm(self, service: str) -> int:
        cfg = self._services.get(service) or self._services.get("default", {})
        return int(cfg.get("requests_per_minute", 60))

    def acquire(self, service: str) -> int:
        """Reserve one slot for ``service``, blocking if the window is full.

        Returns:
            The number of times it had to block (0 if a slot was free) — useful
            for assertions and queue-depth reporting.
        """
        window = self._hits.setdefault(service, deque())
        limit = self._rpm(service)
        blocks = 0
        while True:
            cutoff = self._now() - _WINDOW_SECONDS
            while window and window[0] <= cutoff:
                window.popleft()
            if len(window) < limit:
                window.append(self._now())
                return blocks
            self._sleep(window[0] + _WINDOW_SECONDS - self._now())
            blocks += 1
