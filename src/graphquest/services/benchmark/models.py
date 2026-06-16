"""Benchmark result model — the comparable metrics for both arms."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class BenchmarkRun:
    """Metrics for a single debugging attempt (baseline OR guided).

    Attributes:
        arm: "baseline" or "graph_guided".
        input_tokens: Total prompt tokens consumed.
        output_tokens: Total completion tokens consumed.
        files_read: Number of source files opened.
        units_read: Number of textual units (functions/notes) read.
        iterations: Number of investigation rounds.
        seconds: Wall-clock time to stop.
        cost_usd: Cost from the gatekeeper ledger.
        localized: Whether the root cause was correctly localized.
    """

    arm: str
    input_tokens: int = 0
    output_tokens: int = 0
    files_read: int = 0
    units_read: int = 0
    iterations: int = 0
    seconds: float = 0.0
    cost_usd: float = 0.0
    localized: bool = False

    @property
    def total_tokens(self) -> int:
        """Sum of input and output tokens."""
        return self.input_tokens + self.output_tokens
